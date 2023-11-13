class Context:
    def __init__(self, file: str, code: str, init_index: int, final_index: int):
        self._file = file
        self._code = code
        self._init_index = init_index
        self._final_index = final_index

    def __repr__(self) -> str:
        return f'{self._file}:{self._init_index}-{self._final_index}:{self._code[self._init_index:self._final_index+1]}'
    
    def _get_line(self) -> int:
        return self._code[:self._init_index].count('\n')
    
    def _get_index_column(self, index) -> int:
        if '\n' not in self._code[:index]:
            return index
        return index - self._code[:index].rindex('\n')
    
    def _get_init_column(self) -> int:
        return self._get_index_column(self._init_index)
    
    def _get_final_column(self) -> int:
        return self._get_index_column(self._final_index)
    
    def _get_context_width(self) -> int:
        return self._final_index - self._init_index + 1
    
    def _get_context_line(self) -> str:
        line_init_index = self._code[:self._init_index].rindex('\n') + 1 if '\n' in self._code[:self._init_index] else 0
        line_final_index = self._final_index + self._code[self._final_index:].index('\n') if '\n' in self._code[self._final_index:] else len(self._code)
        return self._code[line_init_index:line_final_index]
    
    def highlight_context_line(self, char: str) -> str:
        line = self._get_line()
        l0 = f' --> {self._file}\n  |'
        l1 = f'{line} | {self._get_context_line()}'
        l2 = ' ' * int(len(str(line))) + ' | ' + ' ' * (self._get_init_column() - 1) + char * self._get_context_width()

        return l0 + '\n' + l1 + '\n' + l2

class ContextualError(Exception):
    def __init__(self, message: str, context: Context):
        super().__init__(message)
        self._context = context

    def get_context(self):
        return self._context
