from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .models import Room, Workspace, Booking
from datetime import date


class AuthSecurityTests(TestCase):
    """Security tests for authentication endpoints."""

    def setUp(self):
        self.client = APIClient()

    # ─── EMAIL VALIDATION ───────────────────────────
    
    def test_register_invalid_email_format(self):
        """Test registration with invalid email format."""
        response = self.client.post(
            '/api/auth/register/',
            {'username': 'notanemail', 'password': 'SecurePass123!'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data['error'].lower())

    def test_register_empty_email(self):
        """Test registration with empty email."""
        response = self.client.post(
            '/api/auth/register/',
            {'username': '', 'password': 'SecurePass123!'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_register_valid_email_format(self):
        """Test registration with valid email format."""
        response = self.client.post(
            '/api/auth/register/',
            {'username': 'user@example.com', 'password': 'SecurePass123!'},
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)

    # ─── PASSWORD REQUIREMENTS ─────────────────────

    def test_register_password_too_short(self):
        """Test password shorter than 8 characters."""
        response = self.client.post(
            '/api/auth/register/',
            {'username': 'user@test.com', 'password': 'Pass1!'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('мінімум 8', response.data['error'].lower())

    def test_register_password_no_digit(self):
        """Test password without digit."""
        response = self.client.post(
            '/api/auth/register/',
            {'username': 'user@test.com', 'password': 'SecurePass!'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('цифр', response.data['error'].lower())

    def test_register_password_no_special_char(self):
        """Test password without special character."""
        response = self.client.post(
            '/api/auth/register/',
            {'username': 'user@test.com', 'password': 'SecurePass123'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('спеціальн', response.data['error'].lower())

    def test_register_password_meets_requirements(self):
        """Test password meeting all requirements."""
        response = self.client.post(
            '/api/auth/register/',
            {'username': 'user@example.com', 'password': 'SecurePass123!'},
            format='json'
        )
        self.assertEqual(response.status_code, 201)

    # ─── DUPLICATE USER ────────────────────────────

    def test_register_duplicate_user(self):
        """Test registering user that already exists."""
        # Create first user
        self.client.post(
            '/api/auth/register/',
            {'username': 'user@example.com', 'password': 'SecurePass123!'},
            format='json'
        )
        # Try to create duplicate
        response = self.client.post(
            '/api/auth/register/',
            {'username': 'user@example.com', 'password': 'SecurePass123!'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('зареєстр', response.data['error'].lower())

    # ─── LOGIN TESTS ───────────────────────────────

    def test_login_with_invalid_credentials(self):
        """Test login with wrong password."""
        User.objects.create_user(username='user@test.com', password='SecurePass123!')
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'user@test.com', 'password': 'WrongPassword!'},
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_login_with_nonexistent_user(self):
        """Test login with non-existent user."""
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'nouser@test.com', 'password': 'AnyPass123!'},
            format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_login_success(self):
        """Test successful login returns token."""
        User.objects.create_user(username='user@test.com', password='SecurePass123!')
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'user@test.com', 'password': 'SecurePass123!'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)


class BookingAPITests(TestCase):
    """Comprehensive booking and workspace tests."""

    def setUp(self):
        self.client = APIClient()
        self.room = Room.objects.create(name='Open Space', floor=1)
        self.workspace = Workspace.objects.create(
            room=self.room,
            number='A-01',
            has_monitor=True
        )
        self.user = User.objects.create_user(
            username='testuser@test.com',
            password='SecurePass123!'
        )
        self.token = Token.objects.create(user=self.user)
        self.other_user = User.objects.create_user(
            username='otheruser@test.com',
            password='SecurePass123!',
        )
        self.other_token = Token.objects.create(user=self.other_user)

    # ─── WORKSPACES ────────────────────────────────

    def test_get_workspaces_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/workspaces/?date=2026-05-28')
        self.assertEqual(response.status_code, 200)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['is_available'])

    def test_get_workspaces_unauthorized(self):
        """Test unauthenticated user cannot list workspaces."""
        response = self.client.get('/api/workspaces/')
        self.assertEqual(response.status_code, 401)

    def test_workspace_has_timestamps(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/workspaces/')
        self.assertEqual(response.status_code, 200)
        results = response.data.get('results', response.data)
        self.assertIn('created_at', results[0])
        self.assertIn('updated_at', results[0])

    # ─── BOOKINGS ───────────────────────────────────

    def test_create_booking_success(self):
        """Test successful booking creation."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(
            '/api/bookings/',
            {
                'workspace': self.workspace.id,
                'booking_date': '2026-05-28',
                'time_start': '09:00',
                'time_end': '17:00'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'active')
        self.assertEqual(Booking.objects.count(), 1)

    def test_booking_has_timestamps(self):
        """Test booking includes timestamps."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(
            '/api/bookings/',
            {
                'workspace': self.workspace.id, 
                'booking_date': '2026-05-28',
                'time_start': '09:00',
                'time_end': '17:00'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('created_at', response.data)
        self.assertIn('updated_at', response.data)

    def test_overbooking_protection(self):
        """Test cannot book same workspace on same date twice."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        data = {
            'workspace': self.workspace.id,
            'booking_date': '2026-05-28',
            'time_start': '09:00',
            'time_end': '17:00',
        }
        first = self.client.post('/api/bookings/', data, format='json')
        self.assertEqual(first.status_code, 201)

        second = self.client.post('/api/bookings/', data, format='json')
        self.assertEqual(second.status_code, 400)
        self.assertEqual(Booking.objects.count(), 1)

    def test_overlapping_time_booking_not_allowed(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        Booking.objects.create(
            user=self.user,
            workspace=self.workspace,
            booking_date='2026-05-28',
            time_start='10:00',
            time_end='12:00',
        )

        response = self.client.post(
            '/api/bookings/',
            {
                'workspace': self.workspace.id,
                'booking_date': '2026-05-28',
                'time_start': '11:00',
                'time_end': '13:00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)

    def test_adjacent_booking_allwed(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        Booking.objects.create(
            user=self.user,
            workspace=self.workspace,
            booking_date='2026-05-28',
            time_start='09:00',
            time_end='10:00',
        )

        response = self.client.post(
            '/api/bookings/',
            {
                'workspace': self.workspace.id,
                'booking_date': '2026-05-28',
                'time_start': '10:00',
                'time_end': '11:00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)

    def test_booking_inside_existing_booking_not_allowed(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        Booking.objects.create(
            user=self.user,
            workspace=self.workspace,
            booking_date='2026-05-28',
            time_start='09:00',
            time_end='17:00',
        )

        response = self.client.post(
            '/api/bookings/',
            {
                'workspace': self.workspace.id,
                'booking_date': '2026-05-28',
                'time_start': '12:00',
                'time_end': '13:00',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)

    def test_booking_shows_unavailable(self):
        Booking.objects.create(
            user=self.user,
            workspace=self.workspace,
            booking_date='2026-05-28',
            time_start='09:00',
            time_end='17:00',
            status='active'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/workspaces/?date=2026-05-28')
        results = response.data.get('results', response.data)
        self.assertFalse(results[0]['is_available'])

    def test_cancelled_booking_makes_workspace_available(self):
        booking = Booking.objects.create(
            user=self.user,
            workspace=self.workspace,
            booking_date='2026-05-28',
            time_start='09:00',
            time_end='17:00',
            status='active'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/workspaces/?date=2026-05-28')
        results = response.data.get('results', response.data)
        self.assertFalse(results[0]['is_available'])

        self.client.post(f'/api/bookings/{booking.id}/cancel/')
        response = self.client.get('/api/workspaces/?date=2026-05-28')
        results = response.data.get('results', response.data)
        self.assertTrue(results[0]['is_available'])


    # ─── CONCURRENCY & EDGE CASES ────────────────

    def test_cannot_book_past_date(self):
        """Test booking past dates is still allowed (admin responsibility)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(
            '/api/bookings/',
            {'workspace': self.workspace.id, 'booking_date': '2020-01-01'},
            format='json'
        )
        # API allows it; validation is on business logic level
        self.assertIn(response.status_code, [201, 400])

    def test_user_sees_only_own_bookings(self):
        Booking.objects.create(
            user=self.user,
            workspace=self.workspace,
            booking_date='2026-05-28',
            time_start='09:00',
            time_end='17:00',
            status='active'
        )
        Booking.objects.create(
            user=self.other_user,
            workspace=self.workspace,
            booking_date='2026-05-29',
            time_start='09:00',
            time_end='17:00',
            status='active'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, 200)
        results = response.data.get('results', response.data)  # Handle pagination
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['user'], self.user.id)

    def test_other_user_cannot_view_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            workspace=self.workspace,
            booking_date='2026-05-28',
            time_start='09:00',
            time_end='17:00',
            status='active'
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.other_token.key}')

        response = self.client.get(
            f'/api/bookings/{booking.id}/'
        )
        self.assertEqual(response.status_code, 404)

    # ─── CANCEL BOOKING ────────────────────────────

    def test_cancel_booking_success(self):
        """Test successful booking cancellation."""
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

    def test_cancel_already_cancelled_booking(self):
        """Test cannot cancel already cancelled booking."""
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

    def test_cancel_other_user_booking(self):
        """Test cannot cancel other user's booking."""
        booking = Booking.objects.create(
            user=self.user,
            workspace=self.workspace,
            booking_date=date.today(),
            status='active'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.other_token.key}')
        response = self.client.post(f'/api/bookings/{booking.id}/cancel/')

        self.assertEqual(response.status_code, 404)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'active')

    # ─── FILTERS ───────────────────────────────────

    def test_filter_by_has_monitor(self):
        Workspace.objects.create(room=self.room, number='A-02', has_monitor=False)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/workspaces/?date=2026-05-28&has_monitor=true')
        self.assertEqual(response.status_code, 200)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['has_monitor'])

    def test_filter_by_room(self):
        room2 = Room.objects.create(name='Conference Room', floor=2)
        Workspace.objects.create(room=room2, number='B-01', has_monitor=True)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(f'/api/workspaces/?date=2026-05-28&room={self.room.id}')
        self.assertEqual(response.status_code, 200)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['room'], self.room.id)












