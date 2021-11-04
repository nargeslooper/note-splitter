"""The class definitions for all the tokens, and a few lists of them.

See a hierarchy of the tokens here:  
https://note-splitter.readthedocs.io/en/latest/token-hierarchy.html
"""


from abc import ABC, abstractmethod
from typing import List, Union, Type, Any
from types import ModuleType
import inspect
from functools import lru_cache
from note_splitter import patterns


def __get_indentation_level(line: str) -> int:
    """Counts the spaces at the start of the line.
    
    If there are tabs instead, each tab is counted as 4 spaces. This
    function assumes tabs and spaces are not mixed.
    """
    level = len(line) - len(line.lstrip(' '))
    if not level:
        tab_count = len(line) - len(line.lstrip('\t'))
        level = tab_count * 4
    return level


class Token(ABC):
    """The abstract base class (ABC) for all tokens.
    
    Each child class must have a ``content`` attribute. If the token
    is not a combination of other tokens, that ``content`` attribute
    must be a string of the original content of the raw line of text.
    Otherwise, the ``content`` attribute is the list of subtokens.
    """
    @abstractmethod
    def __init__(self):
        pass

    def __str__(self):
        """Returns the original content of the token's raw text."""
        return self.content + '\n'


class Block(Token):
    """The ABC for tokens that are each a combination of tokens.
    
    Each child class must have a ``content`` attribute.
    """
    @abstractmethod
    def __init__(self):
        pass

    def __str__(self):
        """Returns the original content of the token's raw text."""
        return ''.join([str(token) for token in self.content])


class TextListItem(Token):
    """The abstract base class (ABC) for text list item tokens.
    
    Each child class must have ``content`` and ``level`` 
    attributes.
    """
    @abstractmethod
    def __init__(self):
        pass


class OrderedListItem(TextListItem):
    """The ABC for an item in an ordered list.
    
    Each child class must have ``content``, ``level``, and 
    ``pattern`` attributes.
    """
    @abstractmethod
    def __init__(self, line: str):
        pass


class TablePart(Token):
    """The ABC for tokens that tables are made out of.
    
    Each child class must have a ``content`` attribute.
    """
    @abstractmethod
    def __init__(self):
        pass


class Fence(Token):
    """The ABC for tokens that block fences are made out of.
    
    Each child class must have a ``content`` attribute.
    """
    @abstractmethod
    def __init__(self):
        pass


class Text(Token):
    """Normal text.
    
    May contain tags.
    
    Attributes
    ----------
    content : str
        The content of the line of text.
    level : int
        The number of spaces of indentation.
    """
    def __init__(self, line: str):
        self.content = line
        self.level = __get_indentation_level(line)


class EmptyLine(Token):
    """A line in a file with either whitespace characters or nothing.
    
    Attributes
    ----------
    content : str
        The content of the line of text.
    pattern : re.Pattern
        The compiled regex pattern for an empty line. This is a class 
        attribute.
    """
    pattern = patterns.empty_line

    def __init__(self, line: str):
        self.content = line


class Header(Token):
    """A header (i.e. a title).
    
    May contain tags.

    Attributes
    ----------
    content : str
        The content of the line of text.
    body : str
        The content of the line of text not including the header 
        symbol(s) and their following whitespace character(s).
    level : int
        The header level. A header level of 1 is the largest possible 
        header.
    pattern : re.Pattern
        The compiled regex pattern for a header. This is a class 
        attribute.
    """
    pattern = patterns.any_header

    def __init__(self, line: str):
        """Parses a line of text and creates a header token."""
        self.content = line
        self.body = line.lstrip('#')
        self.level = len(line) - len(self.body)
        self.body = self.body.lstrip()


class HorizontalRule(Token):
    """A horizontal rule.
    
    Attributes
    ----------
    content : str
        The content of the line of text.
    pattern : re.Pattern
        The compiled regex pattern for a horizontal rule. This is a 
        class attribute.
    """
    pattern = patterns.horizontal_rule

    def __init__(self, line: str):
        self.content = line


class Blockquote(Token):
    """A quote taking up one entire line of text.
    
    May contain tags.

    Attributes
    ----------
    content : str
        The content of the line of text.
    level : int
        The number of spaces of indentation.
    pattern : re.Pattern
        The compiled regex pattern for a blockquote. This is a class 
        attribute.
    """
    pattern = patterns.blockquote

    def __init__(self, line: str):
        self.content = line
        self.level = __get_indentation_level(line)


class BlockquoteBlock(Block):
    """Multiple lines of blockquotes.
    
    Attributes
    ----------
    content : List[Blockquote]
        The consecutive blockquote tokens.
    """
    def __init__(self, tokens_: List[Blockquote]):
        self.content = tokens_


class Footnote(Token):
    """A footnote (not the reference).
    
    May contain tags.

    Attributes
    ----------
    content : str
        The content of the line of text.
    pattern : re.Pattern
        The compiled regex pattern for a footnote. This is a class 
        attribute.
    """
    pattern = patterns.footnote

    def __init__(self, line: str):
        self.content = line


class ToDo(TextListItem):
    """A to do list item that is not completed.
    
    May contain tags.

    Attributes
    ----------
    content : str
        The content of the line of text.
    level : int
        The number of spaces of indentation.
    pattern : re.Pattern
        The compiled regex pattern for a to do list item. This is a 
        class attribute.
    """
    pattern = patterns.to_do

    def __init__(self, line: str):
        self.content = line
        self.level = __get_indentation_level(line)


class Done(TextListItem):
    """A to do list item that is completed.
    
    May contain tags.

    Attributes
    ----------
    content : str
        The content of the line of text.
    level : int
        The number of spaces of indentation.
    pattern : re.Pattern
        The compiled regex pattern for a finished to do list item. This 
        is a class attribute.
    """
    pattern = patterns.done

    def __init__(self, line: str):
        self.content = line
        self.level = __get_indentation_level(line)


class UnorderedListItem(TextListItem):
    """An item in a bullet point list.
    
    May contain tags. The list can have bullet points as asterisks, 
    minuses, and/or pluses.

    Attributes
    ----------
    content : str
        The content of the line of text.
    level : int
        The number of spaces of indentation.
    pattern : re.Pattern
        The compiled regex pattern for an item in an unordered list. 
        This is a class attribute.
    """
    pattern = patterns.unordered_list_item

    def __init__(self, line: str):
        self.content = line
        self.level = __get_indentation_level(line)


class NumberedListItem(OrderedListItem):
    """An item in a numbered list.
    
    May contain tags.

    Attributes
    ----------
    content : str
        The content of the line of text.
    level : int
        The number of spaces of indentation.
    pattern : re.Pattern
        The compiled regex pattern for an item in a numbered list. This 
        is a class attribute.
    """
    pattern = patterns.numbered_list_item

    def __init__(self, line: str):
        self.content = line
        self.level = __get_indentation_level(line)


class LetteredListItem(OrderedListItem):
    """An item in a lettered list.
    
    May contain tags.

    Attributes
    ----------
    content : str
        The content of the line of text.
    level : int
        The number of spaces of indentation.
    pattern : re.Pattern
        The compiled regex pattern for an item in a lettered list. This 
        is a class attribute.
    """
    pattern = patterns.lettered_list_item

    def __init__(self, line: str):
        self.content = line
        self.level = __get_indentation_level(line)


class TextList(Block):
    """A list that is numbered, bullet-pointed, and/or checkboxed.
    
    A single text list may have any combination of ordered list items, 
    unordered list items, to dos, and other text lists with more 
    indentation.

    content : List[Union[TextListItem, 'TextList']]
        The tokens that make up the list. Lists may have sublists.
    level : int
        The number of spaces of indentation of the first item in the 
        list.
    """
    def __init__(self, tokens_: List[Union[TextListItem, 'TextList']] = []):
        self.content = tokens_
        self.level = tokens_[0].level


class TableRow(TablePart):
    """A row of a table.
    
    Attributes
    ----------
    content : str
        The content of the line of text.
    pattern : re.Pattern
        The compiled regex pattern for a table row. This is a class 
        attribute.
    """
    pattern = patterns.table_row

    def __init__(self, line: str):
        self.content = line


class TableDivider(TablePart):
    """The part of a table that divides the table's header from its 
    body.
    
    Attributes
    ----------
    content : str
        The content of the line of text.
    pattern : re.Pattern
        The compiled regex pattern for a table divider. This is a class 
        attribute.
    """
    pattern = patterns.table_divider

    def __init__(self, line: str):
        self.content = line


class Table(Block):
    """A table.
    
    Attributes
    ----------
    content : List[Union[TableRow, TableDivider]]
        The table's row token(s) and possibly divider token(s).
    """
    def __init__(self, tokens_: List[Union[TableRow, TableDivider]]):
        self.content = tokens_


class CodeFence(Fence):
    """The delimiter of a multi-line code block.
    
    Attributes
    ----------
    content : str
        The content of the line of text.
    language : str
        Any text that follows the triple backticks (or triple tildes). 
        Surrounding whitespace characters are removed. This will be an 
        empty string if there are no non-whitespace characters after the
        triple backticks/tildes.
    pattern : re.Pattern
        The compiled regex pattern for a code fence. This is a class 
        attribute.
    """
    pattern = patterns.code_fence

    def __init__(self, line: str):
        self.content = line
        self.language = line.lstrip('~').lstrip('`').strip()


class Code(Token):
    """A line of code inside a code block.
    
    Attributes
    ----------
    content : str
        The content of the line of text.
    """
    def __init__(self, line: str):
        self.content = line


class CodeBlock(Block):
    """A multi-line code block.
    
    Attributes
    ----------
    content : List[Union[CodeFence, Code]]
        The code block's code fence tokens surrounding code token(s).
    language : str
        Any text that follows the triple backticks (or tildes) on the
        line of the opening code fence. Surrounding whitespace 
        characters are removed.
    """
    def __init__(self, tokens_: List[Union[CodeFence, Code]]):
        self.content = tokens_
        self.language = tokens_[0].language


class MathFence(Fence):
    """The delimiter of a multi-line mathblock.
    
    Attributes
    ----------
    content : str
        The content of the line of text.
    pattern : re.Pattern
        The compiled regex pattern for a math fence. This is a class 
        attribute.
    """
    pattern = patterns.math_fence

    def __init__(self, line: str):
        self.content = line


class Math(Token):
    """A line of math inside a math block.
    
    Attributes
    ----------
    content : str
        The content of the line of text.
    """
    def __init__(self, line: str):
        self.content = line


class MathBlock(Block):
    """A multi-line mathblock.

    Inline mathblocks are not supported (the opening and closing math 
    fences must be on different lines).
    
    Attributes
    ----------
    content : List[Math]
        The mathblock's math fence tokens surrounding math token(s).
    """
    def __init__(self, tokens_: List[Union[MathFence, Math]]):
        self.content = tokens_


class Section(Block):
    """A file section starting with a token of the chosen split type.
    
    The Splitter returns a list of Sections. Section tokens never 
    contain section tokens, but may contain tokens of any and all other 
    types.

    Attributes
    ----------
    content : List[Token]
        The tokens in this section, starting with a token of the chosen 
        split type.
    """
    def __init__(self, tokens_: List[Token]):
        self.content = tokens_


# Some lines of text can be categorized without looking at their 
# context. Each type in the list below must have a pattern attribute.
simple_token_types = [
    EmptyLine,
    Header,
    HorizontalRule,
    CodeFence,
    MathFence,
    Blockquote,
    ToDo,
    Done,
    Footnote,
    UnorderedListItem,
    NumberedListItem,
    LetteredListItem,
    TableDivider,
    TableRow,
]


# These are types whose content can contain tags.
tag_containing_types = (
    Text,
    Header,
    Blockquote,
    Footnote,
    ToDo,
    Done,
    UnorderedListItem,
    NumberedListItem,
    LetteredListItem,
)


def __is_token_type(obj: Any) -> bool:
    """Returns True if obj is a Token type.
    
    Parameters
    ----------
    obj : Any
        The object to test.
    """
    return inspect.isclass(obj) and obj.__name__ not in ('ABC', 'module')


@lru_cache(maxsize=1)
def get_all_token_types(tokens_module: ModuleType) -> List[Type[Token]]:
    """Gets the list of all token types.
    
    Call the function like this: ``tokens.get_all_token_types(tokens)``.

    Parameters
    ----------
    tokens_module : ModuleType
        The module containing the token types. There is only one correct
        argument. The only reason why the argument is required is 
        because there doesn't seem to be any other way to automatically 
        get the list of token types from within the file they are in.
    """
    return [c[1] for c in inspect.getmembers(tokens_module, __is_token_type)]
