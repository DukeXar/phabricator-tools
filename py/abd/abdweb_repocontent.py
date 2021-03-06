"""Render html to report the state of a repository watched by Arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdweb_repocontent
#
# Public Functions:
#   render
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import abdt_reporeporter


def render(formatter, repo_report, branch_report):

    if not repo_report and not branch_report:
        formatter.text('repo has never been tried')
        return

    _render_repo_report(formatter, repo_report)
    formatter.section_break()
    formatter.horizontal_rule()
    _render_branch_report(formatter, branch_report)


def _render_repo_report(formatter, repo_report):
    if not repo_report:
        return

    repo_name = repo_report[abdt_reporeporter.REPO_ATTRIB_NAME]
    status = repo_report[abdt_reporeporter.REPO_ATTRIB_STATUS]
    branch = repo_report[abdt_reporeporter.REPO_ATTRIB_STATUS_BRANCH]
    status_text = repo_report[abdt_reporeporter.REPO_ATTRIB_STATUS_TEXT]

    formatter.heading(repo_name)

    if status == abdt_reporeporter.REPO_STATUS_OK:
        divclass = 'greeninset'
    elif status == abdt_reporeporter.REPO_STATUS_UPDATING:
        divclass = 'activeinset'
    else:
        divclass = 'redinset'

    with formatter.singletag_context('div', class_=divclass):
        formatter.text('repo status: ' + status)
        if branch:
            formatter.text('branch: ' + branch)
        if status_text:
            formatter.text('status text:\n' + status_text)


def _render_branch_report(formatter, branch_report):
    if not branch_report:
        return

    branches = branch_report[abdt_reporeporter.RESULT_ATTRIB_BRANCHES]
    for branch in branches:
        name = branch[abdt_reporeporter.RESULT_BRANCH_NAME]
        status = branch[abdt_reporeporter.RESULT_BRANCH_STATUS]
        branch_url = branch[abdt_reporeporter.RESULT_BRANCH_BRANCH_URL]
        review_url = branch[abdt_reporeporter.RESULT_BRANCH_REVIEW_URL]
        notes = branch[abdt_reporeporter.RESULT_BRANCH_NOTES]

        if status == abdt_reporeporter.RESULT_BRANCH_STATUS_OK:
            divclass = 'greencard'
        else:
            divclass = 'redcard'

        with formatter.singletag_context('div', class_=divclass):
            formatter.heading(name)
            if branch_url:
                formatter.link(branch_url, 'view branch')
                formatter.section_break()
            if review_url:
                formatter.link(review_url, 'view review')
                formatter.section_break()
            if notes:
                formatter.text(notes)


#------------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#------------------------------- END-OF-FILE ----------------------------------
