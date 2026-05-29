from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .models import Room, Workspace, Booking
from datetime import date


class BookingAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()


        self.room = Room.objects.create(
            name='Open Space',
            floor=1
        )
        self.workspace = Workspace.objects.create(
            room=self.room,
            number='A-01',
            has_monitor=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)


        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123',
        )
        self.other_token = Token.objects.create(user=self.other_user)


    # ─── РЕЄСТРАЦІЯ ────────────────────────────────

    def test_register_success(self):
        response = self.client.post(
            '/api/auth/register/',
            {'username': 'newuser', 'password': 'newpass123'},
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)

    def test_register_duplicate_username(self):
        response = self.client.post(
            '/api/auth/register/',
            {'username': 'testuser', 'password': 'pass'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    # ─── ЛОГІН ─────────────────────────────────────

    def test_login_success(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'testuser', 'password': 'testpass123'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_login_wrong_password(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'testuser', 'password': 'wrongpass'},
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    # ─── РОБОЧІ МІСЦЯ ──────────────────────────────

    def test_get_workspaces_authenticated(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        response = self.client.get(
            '/api/workspaces/?date=2026-05-28'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]['is_available'])

    def test_get_workspaces_unauthorized(self):
        response = self.client.get('/api/workspaces/')
        self.assertEqual(response.status_code, 401)

    # ─── БРОНЮВАННЯ ────────────────────────────────

    def test_create_booking_success(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        response = self.client.post(
            '/api/bookings/',
            {'workspace': self.workspace.id, 'booking_date': '2026-05-28'},
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'active')
        self.assertEqual(Booking.objects.count(), 1)

    def test_overbooking_protection(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        data = {
            'workspace': self.workspace.id,
            'booking_date': '2026-05-28',
        }
        first = self.client.post('/api/bookings/', data, format='json')
        self.assertEqual(first.status_code, 201)

        second = self.client.post('/api/bookings/', data, format='json')
        self.assertEqual(second.status_code, 400)
        self.assertEqual(Booking.objects.count(), 1)

    def test_booking_shows_unavailable(self):
        Booking.objects.create(
            user=self.user,
            workspace=self.workspace,
            booking_date='2026-05-28',
            status='active'
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        response = self.client.get(
            '/api/workspaces/?date=2026-05-28',
        )
        self.assertFalse(response.data[0]['is_available'])

    # ─── СКАСУВАННЯ ────────────────────────────────

    def test_cancel_success(self):
        booking = Booking.objects.create(
            user=self.user,
            workspace=self.workspace,
            booking_date='2026-05-28',
            status='active',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(f'/api/bookings/{booking.id}/cancel/')

        self.assertEqual(response.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')

    def test_cancel_already_cancelled(self):
        booking = Booking.objects.create(
            user=self.user,
            workspace=self.workspace,
            booking_date='2026-05-28',
            status='cancelled',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(f'/api/bookings/{booking.id}/cancel/')

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_cancel_other_user(self):
        booking = Booking.objects.create(
            user=self.user,
            workspace=self.workspace,
            booking_date=date.today(),
            status='active'
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.other_token.key}'
        )

        response = self.client.post(
            f'/api/bookings/{booking.id}/cancel/',
        )

        self.assertEqual(response.status_code, 404)

        booking.refresh_from_db()
        self.assertEqual(booking.status, 'active')

    # ─── ФІЛЬТРАЦІЯ ────────────────────────────────

    def test_filter_by_has_monitor(self):
        # Додаємо робочі місця з та без монітора
        workspace_no_monitor = Workspace.objects.create(
            room=self.room,
            number='A-02',
            has_monitor=False
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        # Фільтруємо тільки з монітором
        response = self.client.get(
            '/api/workspaces/?date=2026-05-28&has_monitor=true'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]['has_monitor'])

    def test_filter_by_room(self):
        # Додаємо другу кімнату й робоче місце в ній
        room2 = Room.objects.create(
            name='Conference Room',
            floor=2
        )
        workspace2 = Workspace.objects.create(
            room=room2,
            number='B-01',
            has_monitor=True
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        # Фільтруємо за першою кімнатою
        response = self.client.get(
            f'/api/workspaces/?date=2026-05-28&room={self.room.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['room'], self.room.id)













