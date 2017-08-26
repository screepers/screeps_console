from bisect import bisect_left
import pkg_resources
import urwid


class Autocomplete(object):

    lists = {}

    def __init__(self, comp):
        self.comp = comp

        basic = self.loadList('basic')
        constants = self.loadList('constants')
        combined = basic + constants
        self.lists['combined'] = self.sortList(combined)
        return


    def loadList(self, listname):

        if not listname in self.lists:
            autocomplete = pkg_resources.resource_string(__name__, 'data/autocomplete/' + listname + '.dat').decode("utf-8")
            autocomplete_list = autocomplete.splitlines()
            autocomplete_list_unique = self.sortList(autocomplete_list)
            self.lists[listname] = autocomplete_list_unique
        return self.lists[listname]


    def sortList(self, lst):
        autocomplete_list_filtered = (x for x in lst if not x.startswith('#') and x != '')
        autocomplete_list_unique = sorted(set(autocomplete_list_filtered))
        return autocomplete_list_unique


    def complete(self):
        prefix = ''
        user_text = self.comp.edit.get_edit_text()
        results = self.getMatchingString(self.loadList('combined'), user_text)
        number_results = len(results)

        # Check for a '.' to see if we're looking at a property
        if number_results <= 0:
            if '.' in user_text:
                pos = user_text.rfind('.')
                prefix = user_text[:pos+1]
                string = user_text[pos+1:]
                results = self.getMatchingString(self.loadList('properties'), string)
                number_results = len(results)


        if number_results <= 0:
            return False
        elif number_results == 1:
            new_edit = prefix + results[0] + ' '
            self.comp.edit.set_edit_text(new_edit)
            self.comp.edit.set_edit_pos(len(new_edit))
        elif number_results > 1:
            bestMatch = self.getStringOverlapFromList(results)
            new_edit = prefix + bestMatch
            self.comp.edit.set_edit_text(new_edit)
            self.comp.edit.set_edit_pos(len(new_edit))
            self.comp.listwalker.append(urwid.Text(('logged_response', ' * '.join(results))))
            self.comp.listbox.autoscroll()
        return False



    def getMatchingString(self, wordlist, word_fragment):
        if len(word_fragment) <= 0:
            return []
        return wordlist[bisect_left(wordlist, word_fragment):
         bisect_left(wordlist, word_fragment[:-1] + chr(ord(word_fragment[-1])+1))]


    def getStringOverlapFromList(self, wordlist):
        for index,item in enumerate(wordlist):
            if index == 0:
                returnString = item
            else:
                returnString = self.getStringOverlap(returnString, item)
        return returnString


    def getStringOverlap(self, a, b):
        matchString = ''
        for index, char in enumerate(a):
            if char == b[index]:
                matchString = matchString + char
            else:
                return matchString

        return matchString
