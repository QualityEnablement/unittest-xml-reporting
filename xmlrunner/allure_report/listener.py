import allure_commons
from allure_commons.utils import host_tag, thread_tag
from allure_commons.utils import md5
# Going to use for Allure class
from allure_commons.reporter import AllureReporter
from allure_commons.types import LabelType, LinkType
from allure_commons.model2 import TestResult
from allure_commons.model2 import Parameter, Label, Link, StatusDetails, Status, Attachment
from allure_commons.utils import uuid4
from allure_commons.utils import now
from allure_commons.utils import platform_label

# -------------------------------------------------
from xmlrunner.allure_report.utils import get_suit_name, fullname, name, labels, params


class AllureListener:

    def __init__(self):
        # need to add config here
        self._host = host_tag()
        self._thread = thread_tag()
        self.reporter = AllureReporter()
        self.current_test_uuid = None

    def start_test(self, test):
        self.current_test_uuid = uuid4()
        test_case = TestResult(uuid=self.current_test_uuid, start=now())
        test_case.name = name(test)
        test_case.fullName = fullname(test)
        test_case.testCaseId = md5(test_case.fullName)
        test_case.historyId = md5(test.id())
        test_case.status = Status.PASSED
        test_case.labels.extend(labels(test))
        test_case.labels.append(Label(name=LabelType.HOST, value=self._host))
        test_case.labels.append(Label(name=LabelType.THREAD, value=self._thread))
        test_case.labels.append(Label(name=LabelType.FRAMEWORK, value='unittest'))
        test_case.labels.append(Label(name=LabelType.LANGUAGE, value='python'))
        test_case.labels.append(Label(name=LabelType.LANGUAGE, value=platform_label()))
        test_case.labels.append(Label(name=LabelType.PARENT_SUITE, value=test.DOMAIN))
        test_case.labels.append(Label(name=LabelType.SUB_SUITE, value=get_suit_name(test)))
        test_case.parameters = params(test)
        self.reporter.schedule_test(self.current_test_uuid, test_case)

    def stop_test(self, test):
        test_case = self.reporter.get_test(None)
        test_case.attachments.append(
            Attachment(name=f"{get_suit_name(test)}.log", source=f"{get_suit_name(test)}.log", type="text/plain"))
        test_case.stop = now()
        self.reporter.close_test(self.current_test_uuid)

    def add_failure(self, test, err, info_traceback, message="The test is failed"):
        screenshot_name = get_suit_name(test) + '_' + name(test)
        test_case = self.reporter.get_test(None)
        test_case.statusDetails = StatusDetails(message=message, trace=info_traceback)
        test_case.attachments.append(
            Attachment(name=screenshot_name, source=f"{screenshot_name}.png", type="image/png"))
        test_case.status = Status.FAILED
        self.reporter.schedule_test(self.current_test_uuid, test_case)

    def add_error(self, test, err, info_traceback, message="The test is error"):
        test_case = self.reporter.get_test(None)
        test_case.statusDetails = StatusDetails(message=message, trace=info_traceback)
        screenshot_name = get_suit_name(test) + '_' + name(test)
        test_case.attachments.append(
            Attachment(name=screenshot_name, source=f"{screenshot_name}.png", type="image/png"))
        test_case.status = Status.BROKEN
        self.reporter.schedule_test(self.current_test_uuid, test_case)

    # Allure Hooks Spec
    @allure_commons.hookimpl
    def add_title(self, test_title):
        test_case = self.reporter.get_test(None)
        if test_case:
            test_case.name = test_title

    @allure_commons.hookimpl
    def add_description(self, test_description):
        test_result = self.reporter.get_test(None)
        if test_result:
            test_result.description = test_description

    @allure_commons.hookimpl
    def add_description_html(self, test_description_html):
        test_case = self.reporter.get_test(None)
        if test_case:
            test_case.descriptionHtml = test_description_html

    @allure_commons.hookimpl
    def attach_data(self, body, name, attachment_type, extension):
        self.reporter.attach_data(self.current_test_uuid, body, name=name, attachment_type=attachment_type,
                                  extension=extension)

    @allure_commons.hookimpl
    def attach_file(self, source, name, attachment_type, extension):
        self.reporter.attach_file(self.current_test_uuid, source, name=name, attachment_type=attachment_type,
                                  extension=extension)

    #
    @allure_commons.hookimpl
    def add_link(self, url, link_type, name):
        test_case = self.reporter.get_test(None)
        test_case.links.append(Link(link_type, url, name))
