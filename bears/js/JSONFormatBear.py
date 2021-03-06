import json
from collections import OrderedDict

from coalib.bearlib import deprecate_settings
from coalib.bearlib.spacing.SpacingHelper import SpacingHelper
from coalib.bears.LocalBear import LocalBear
from coalib.results.Diff import Diff
from coalib.results.Result import Result
from coala_utils.param_convertion import negate


class JSONFormatBear(LocalBear):
    try:
        DecodeError = json.decoder.JSONDecodeError
    except AttributeError:
        DecodeError = ValueError

    LANGUAGES = {"JSON"}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Formatting'}

    @deprecate_settings(indent_size='tab_width',
                        escape_unicode=('keep_unicode', negate))
    def run(self, filename, file,
            json_sort: bool=False,
            indent_size: int=SpacingHelper.DEFAULT_TAB_WIDTH,
            escape_unicode: bool=True):
        """
        Raises issues for any deviations from the pretty-printed JSON.

        :param json_sort:      Whether or not keys should be sorted.
        :param indent_size:    Number of spaces per indentation level.
        :param escape_unicode: Whether or not to escape unicode values using
                               ASCII.
        """
        try:
            json_content = json.loads(''.join(file),
                                      object_pairs_hook=OrderedDict)
        except self.DecodeError as err:
            yield Result.from_values(
                self,
                "This file does not contain parsable JSON. " + repr(str(err)),
                file=filename)
            return

        corrected = json.dumps(json_content,
                               sort_keys=json_sort,
                               indent=indent_size,
                               ensure_ascii=escape_unicode
                               ).splitlines(True)
        # Because of a bug in several python versions we have to correct
        # whitespace here.
        corrected = tuple(line.rstrip(" \n") + "\n" for line in corrected)
        diff = Diff.from_string_arrays(file, corrected)

        if len(diff) > 0:
            yield Result(self,
                         "This file can be reformatted by sorting keys and "
                         "following indentation.",
                         affected_code=tuple(d.range(filename)
                                             for d in diff.split_diff()),
                         diffs={filename: diff})
