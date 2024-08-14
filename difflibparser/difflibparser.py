import difflib

class DiffCode:
    SIMILAR = 0         # starts with '  '
    RIGHTONLY = 1       # starts with '+ '
    LEFTONLY = 2        # starts with '- '
    CHANGED = 3         # either three or four lines with the prefixes ('-', '+', '?'), ('-', '?', '+') or ('-', '?', '+', '?') respectively

class DifflibParser:
    def __init__(self, text1, text2, method="Inline"):
        self.__text1 = text1
        self.__text2 = text2
        self.method = method

        if self.method == "Side by Side":
            self.__diff = list(difflib.ndiff(self.__text1, self.__text2))
        elif self.method == "Diff Only":
            self.__diff = list(difflib.unified_diff(self.__text1, self.__text2, lineterm=''))
        elif self.method == "Complete File":
            self.__diff = list(difflib.context_diff(self.__text1, self.__text2, lineterm=''))
        else:  # Default to Inline
            self.__diff = list(difflib.ndiff(self.__text1, self.__text2))

        self.__currentLineno = 0

    def __iter__(self):
        return self

    def __next__(self):
        result = {}
        if self.__currentLineno >= len(self.__diff):
            raise StopIteration
        currentLine = self.__diff[self.__currentLineno]

        if self.method == "Side by Side":
            result['line'] = currentLine
            result['code'] = None
        else:
            code = currentLine[:2]
            line = currentLine[2:]
            result['line'] = line
            if code == '  ':
                result['code'] = DiffCode.SIMILAR
            elif code == '- ':
                incrementalChange = self.__tryGetIncrementalChange(self.__currentLineno)
                if not incrementalChange:
                    result['code'] = DiffCode.LEFTONLY
                else:
                    result['code'] = DiffCode.CHANGED
                    result['leftchanges'] = incrementalChange.get('left', [])
                    result['rightchanges'] = incrementalChange.get('right', [])
                    result['newline'] = incrementalChange.get('newline', '')
                    self.__currentLineno += incrementalChange.get('skiplines', 0)
            elif code == '+ ':
                result['code'] = DiffCode.RIGHTONLY

        self.__currentLineno += 1
        return result

    def __tryGetIncrementalChange(self, lineno):
        lineOne = self.__diff[lineno] if lineno < len(self.__diff) else None
        lineTwo = self.__diff[lineno + 1] if lineno + 1 < len(self.__diff) else None
        lineThree = self.__diff[lineno + 2] if lineno + 2 < len(self.__diff) else None
        lineFour = self.__diff[lineno + 3] if lineno + 3 < len(self.__diff) else None

        changes = {}
        if lineOne and lineOne[:2] == '- ' and \
           lineTwo and lineTwo[:2] == '? ' and \
           lineThree and lineThree[:2] == '+ ' and \
           lineFour and lineFour[:2] == '? ':
            changes['left'] = [i for (i,c) in enumerate(lineTwo[2:]) if c in ['-', '^']]
            changes['right'] = [i for (i,c) in enumerate(lineFour[2:]) if c in ['+', '^']]
            changes['newline'] = lineThree[2:]
            changes['skiplines'] = 3
            return changes
        elif lineOne and lineOne[:2] == '- ' and \
           lineTwo and lineTwo[:2] == '+ ' and \
           lineThree and lineThree[:2] == '? ':
            changes['right'] = [i for (i,c) in enumerate(lineThree[2:]) if c in ['+', '^']]
            changes['left'] = []
            changes['newline'] = lineTwo[2:]
            changes['skiplines'] = 2
            return changes
        elif lineOne and lineOne[:2] == '- ' and \
           lineTwo and lineTwo[:2] == '? ' and \
           lineThree and lineThree[:2] == '+ ':
            changes['right'] = []
            changes['left'] = [i for (i,c) in enumerate(lineTwo[2:]) if c in ['-', '^']]
            changes['newline'] = lineThree[2:]
            changes['skiplines'] = 2
            return changes
        else:
            return None
