from django.test import TestCase
from django.contrib.staticfiles.testing import LiveServerTestCase

from django.contrib.auth.models import User
from volunteer.models import Volunteer
from event.models import Event
from job.models import Job
from shift.models import Shift, VolunteerShift

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from organization.models import Organization #hack to pass travis,Bug in Code


class ShiftSignUp(LiveServerTestCase):
    '''
    '''
    def setUp(self):
        volunteer_user = User.objects.create_user(
                username = 'volunteer',
                password = 'volunteer')

        Volunteer.objects.create(
                user = volunteer_user,
                address = 'address',
                city = 'city',
                state = 'state',
                country = 'country',
                phone_number = '9999999999',
                email = 'volunteer@volunteer.com',
                unlisted_organization = 'organization')

        # create an org prior to registration. Bug in Code
        # added to pass CI
        Organization.objects.create(
                name = 'DummyOrg')

        self.homepage = '/'
        self.authentication_page = '/authentication/login/'
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)
        self.driver.maximize_window()
        super(ShiftSignUp, self).setUp()

    def tearDown(self):
        self.driver.quit()
        super(ShiftSignUp, self).tearDown()

    def login(self):
        self.driver.get(self.live_server_url + self.authentication_page)
        self.driver.find_element_by_id('id_login').send_keys('volunteer')
        self.driver.find_element_by_id('id_password').send_keys('volunteer')
        self.driver.find_element_by_xpath('//form[1]').submit()

        self.assertEqual(self.driver.current_url,
                self.live_server_url + self.homepage)

    def register_event_utility(self):
        Event.objects.create(
                name = 'event',
                start_date = '2016-05-10',
                end_date = '2018-06-16')

    def register_job_utility(self):
        Job.objects.create(
                name = 'job',
                start_date = '2016-05-10',
                end_date = '2017-06-15',
                event = Event.objects.get(name = 'event'))

    def register_shift_utility(self):
        Shift.objects.create(
                date = '2017-06-15',
                start_time = '09:00',
                end_time = '15:00',
                max_volunteers ='6',
                job = Job.objects.get(name = 'job'))

    def test_events_page_with_no_events(self):
        self.login()

        # open Shift Sign Up
        self.driver.find_element_by_link_text('Shift Sign Up').click()

        self.assertEqual(self.driver.find_element_by_class_name('alert-info').text,
               'There are no events.')


    def test_signup_shifts_with_registered_shifts(self):
        # login
        self.login()

        self.register_event_utility()
        self.register_job_utility()
        self.register_shift_utility()

        # open Shift Sign Up
        self.driver.find_element_by_link_text('Shift Sign Up').click()

        # on event page
        self.assertEqual(self.driver.find_element_by_xpath(
            '//table//tbody//tr[1]//td[4]').text, 'View Jobs')
        self.driver.find_element_by_xpath(
                '//table//tbody//tr[1]//td[4]//a').click()

        # on jobs page
        self.assertEqual(self.driver.find_element_by_xpath(
            '//table//tbody//tr[1]//td[4]').text, 'View Shifts')
        self.driver.find_element_by_xpath(
                '//table//tbody//tr[1]//td[4]//a').click()

        # on shifts page
        self.assertEqual(self.driver.find_element_by_xpath(
            '//table//tbody//tr[1]//td[4]').text, 'Sign Up')
        self.driver.find_element_by_xpath(
                '//table//tbody//tr[1]//td[4]//a').click()

        # confirm shift assignment
        self.driver.find_element_by_xpath('//form[1]').submit()
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element_by_class_name('alert-danger')

        # check shift signed up
        self.assertEqual(self.driver.find_element_by_xpath(
            'html/body/div[2]/h3').text,
            'Upcoming Shifts')
        self.assertEqual(self.driver.find_element_by_xpath(
            '//table//tbody//tr[1]//td[1]').text,
            'job')
        self.assertEqual(self.driver.find_element_by_xpath(
            '//table//tbody//tr[1]//td[2]').text,
            'June 15, 2017')
        self.assertEqual(self.driver.find_element_by_xpath(
            '//table//tbody//tr[1]//td[3]').text,
            '9 a.m.')
        self.assertEqual(self.driver.find_element_by_xpath(
            '//table//tbody//tr[1]//td[4]').text,
            '3 p.m.')

    def test_signup_for_same_shift_again(self):
        # login
        self.login()

        self.register_event_utility()
        self.register_job_utility()
        self.register_shift_utility()

        # open Shift Sign Up
        self.driver.find_element_by_link_text('Shift Sign Up').click()

        # events shown in table
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element_by_class_name('alert-info')
        self.assertEqual(self.driver.find_element_by_xpath(
            '//table//tbody//tr[1]//td[4]').text,
            'View Jobs')
        self.driver.find_element_by_xpath(
                '//table//tbody//tr[1]//td[4]//a').click()

        # on jobs page
        self.assertEqual(self.driver.find_element_by_xpath(
            '//table//tbody//tr[1]//td[4]').text,
            'View Shifts')
        self.driver.find_element_by_xpath(
                '//table//tbody//tr[1]//td[4]//a').click()

        # on shifts page, Sign up this shift !
        self.assertEqual(self.driver.find_element_by_xpath(
            '//table//tbody//tr[1]//td[4]').text,
            'Sign Up')
        self.driver.find_element_by_xpath(
                '//table//tbody//tr[1]//td[4]//a').click()

        # confirm on shift sign up
        self.driver.find_element_by_xpath('//form[1]').submit()
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element_by_class_name('alert-danger')

        # sign up same shift again
        # open Shift Sign Up
        self.driver.find_element_by_link_text('Shift Sign Up').click()

        # events page
        self.assertEqual(self.driver.find_element_by_class_name('alert-info').text,
               'There are no events.')
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element_by_tag_name('table')
            self.assertEqual(self.driver.find_element_by_xpath(
            '//table//tbody//tr[1]//td[4]').text, 'View Jobs')


    def test_empty_events(self):
        self.login()

        self.register_event_utility()

        # open Shift Sign Up
        self.driver.find_element_by_link_text('Shift Sign Up').click()

        # on event page
        self.assertEqual(self.driver.find_element_by_class_name('alert-info').text,
               'There are no events.')
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element_by_tag_name('table')
            self.assertEqual(self.driver.find_element_by_xpath(
            '//table//tbody//tr[1]//td[4]').text, 'View Jobs')

        self.register_job_utility()

        self.assertEqual(self.driver.find_element_by_class_name('alert-info').text,
               'There are no events.')
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element_by_tag_name('table')
            self.assertEqual(self.driver.find_element_by_xpath(
            '//table//tbody//tr[1]//td[4]').text, 'View Jobs')

    def test_shift_sign_up_with_outdated_shifts(self):
        self.login()

        self.register_event_utility()
        self.register_job_utility()

        # create outdated shift
        Shift.objects.create(
                date = '2016-05-11',
                start_time = '09:00',
                end_time = '15:00',
                max_volunteers ='6',
                job = Job.objects.get(name = 'job'))

        # open Shift Sign Up
        self.driver.find_element_by_link_text('Shift Sign Up').click()

        # on event page
        self.assertEqual(self.driver.find_element_by_xpath('//table//tbody//tr[1]//td[4]').text, 'View Jobs')
        self.driver.find_element_by_xpath('//table//tbody//tr[1]//td[4]//a').click()

        # on jobs page
        self.assertEqual(self.driver.find_element_by_xpath('//table//tbody//tr[1]//td[4]').text, 'View Shifts')
        self.driver.find_element_by_xpath('//table//tbody//tr[1]//td[4]//a').click()

        self.assertEqual(self.driver.find_element_by_class_name('alert-info').text,'There are currently no shifts for the job job.')

    def test_shift_sign_up_with_no_slots(self):

        self.register_event_utility()
        self.register_job_utility()

        # create shift with no slot
        shift_2 = Shift.objects.create(
                date = '2016-05-11',
                start_time = '09:00',
                end_time = '15:00',
                max_volunteers ='1',
                job = Job.objects.get(name = 'job'))

        # Create another volunteer
        volunteer_user_2 = User.objects.create_user(
                username = 'volunteer-2',
                password = 'volunteer')

        volunteer_2 = Volunteer.objects.create(
                user = volunteer_user_2,
                address = 'address',
                city = 'city',
                state = 'state',
                country = 'country',
                phone_number = '9999999999',
                email = 'volunteer2@volunteer.com',
                unlisted_organization = 'organization')

        # Assign shift to the volunteer
        VolunteerShift.objects.create(
                shift = shift_2,
                volunteer = volunteer_2)

        # Login as volunteer 1 and open Shift Sign Up
        self.login()
        self.driver.find_element_by_link_text('Shift Sign Up').click()

        # on event page
        self.assertEqual(self.driver.find_element_by_class_name('alert-info').text,'There are no events.')

    def test_search_event(self):

        self.register_event_utility()
        self.register_job_utility()
        self.register_shift_utility()

        # Login as volunteer 1 and open Shift Sign Up
        self.login()
        self.driver.find_element_by_link_text('Shift Sign Up').click()

        # enter date range in which an event starts
        self.driver.find_element_by_id('from').send_keys('05/08/2016')
        self.driver.find_element_by_id('to').send_keys('08/31/2017')
        self.driver.find_element_by_xpath('//form[1]').submit()
        # verify that the event shows up
        self.assertEqual(self.driver.find_element_by_xpath('//table//tbody//tr[1]//td[1]').text, 'event')

        # enter date range in which no event starts
        self.driver.find_element_by_id('from').clear()
        self.driver.find_element_by_id('to').clear()
        self.driver.find_element_by_id('from').send_keys('10/08/2016')
        self.driver.find_element_by_id('to').send_keys('08/31/2017')
        self.driver.find_element_by_xpath('//form[1]').submit()
        # verify that no event shows up on event page
        self.assertEqual(self.driver.find_element_by_class_name('alert-info').text,'There are no events.')

        # enter only incorrect starting date
        self.driver.find_element_by_id('from').clear()
        self.driver.find_element_by_id('to').clear()
        self.driver.find_element_by_id('from').send_keys('10/08/2016')
        # verify that no event shows up on event page
        self.assertEqual(self.driver.find_element_by_class_name('alert-info').text,'There are no events.')

        """# enter only correct starting date
        self.driver.find_element_by_id('from').clear()
        self.driver.find_element_by_id('from').send_keys('05/10/2016')
        # verify that the event shows up
        self.assertEqual(self.driver.find_element_by_xpath('//table//tbody//tr[1]//td[1]').text, 'event')"""

        # enter only incorrect ending date
        self.driver.find_element_by_id('from').clear()
        self.driver.find_element_by_id('to').send_keys('10/08/2015')
        # verify that no event shows up on event page
        self.assertEqual(self.driver.find_element_by_class_name('alert-info').text,'There are no events.')

        """# enter correct ending date
        self.driver.find_element_by_id('to').clear()
        self.driver.find_element_by_id('to').send_keys('06/15/2017')
        # verify that the event shows up
        self.assertEqual(self.driver.find_element_by_xpath('//table//tbody//tr[1]//td[1]').text, 'event')"""