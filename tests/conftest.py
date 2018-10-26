import allure
import pytest

from globals.jira_globals import *


@allure.step("Getting web driver")
@pytest.fixture(scope="session")
def get_driver():
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    web_driver = webdriver.Chrome(ChromeDriverManager().install())
    yield web_driver
    web_driver.close()


@allure.step("Getting login page")
@pytest.fixture(scope="class")
def get_login_page(get_driver):
    from src.pages.login_page import LoginPage
    return LoginPage(get_driver)


@allure.step("Getting new issue page")
@pytest.fixture(scope="class")
def get_new_issue_page(get_driver):
    from src.pages.new_issue_page import NewIssuePage
    return NewIssuePage(get_driver)


@allure.step("Getting search page")
@pytest.fixture(scope="class")
def get_search_page(get_driver):
    from src.pages.search_page import SearchPage
    return SearchPage(get_driver)


@allure.step("Getting edit issue page")
@pytest.fixture(scope="class")
def get_edit_issue_page(get_driver):
    from src.pages.edit_issue_page import EditIssuePage
    return EditIssuePage(get_driver)


@allure.step("Getting issue summary page")
@pytest.fixture(scope="class")
def get_issue_summary_page(get_driver):
    from src.pages.issue_summary_page import IssueSummaryPage
    return IssueSummaryPage(get_driver)


@allure.step("Login to Jira before tests started and logout after tests finished")
@pytest.fixture(scope="function")
def login_to_jira(get_driver):
    from src.pages.login_page import LoginPage
    login_page = LoginPage(get_driver)
    with allure.step("Open login page"):
        login_page.open()
    with allure.step("Login to JIRA"):
        main_page = login_page.login(login, password)
    yield main_page.wait_until_page_is_loaded(15)
    with allure.step("Logout from JIRA"):
        main_page.logout()


@allure.step("Cleanup Jira from issues reported by test user")
@pytest.fixture(scope="class")
def jira_test_data():
    from rest.jira_web_service import JiraWebService

    test_data = (("Maxim test issue 1", "Maxim test issue", "Bug", "Low", ""),
                 ("Maxim test issue 2", "Maxim test issue", "User Story", "High", ""),
                 ("Maxim test issue 3", "Maxim test issue", "Test", "Medium", ""),
                 ("Maxim test issue 4", "Maxim test issue", "Task", "Lowest", ""),
                 ("Maxim test issue 5", "Maxim test issue", "Story", "Highest", ""))

    with allure.step("Create new issues"):
        for record in test_data:
            JiraWebService.create_new_issue(*record)

    yield

    with allure.step("Call search issue method"):
        r = JiraWebService.search_issues_by_jql(
            "reporter = " + login,
            ["id"])
    with allure.step("Delete all created issues"):
        for issue in r.json()['issues']:
            JiraWebService.delete_issue_by_id(issue.get('id'))


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)
