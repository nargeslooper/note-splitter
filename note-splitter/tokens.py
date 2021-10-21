# external imports
from abc import ABC, abstractmethod
from typing import List, Union

# internal imports
import patterns


def get_indentation_level(line: str) -> int:
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
    
    Each child class must have a :code:`content` attribute. If the token
    is not a combination of other tokens, that :code:`content` attribute
    must be a string of the original content of the raw line of text.
    Otherwise, the :code:`content` attribute is the list of subtokens.
    """
    @abstractmethod
    def raw(self):
        """Returns the original content of the token's raw text."""
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
        self.level = get_indentation_level(line)

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        return self.content + '\n'


# TODO: create an EmptyLine token class.


class Header(Token):
    """A header (i.e. a title).
    
    May contain tags.

    Attributes
    ----------
    content : str
        The content of the line of text.
    title : str
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
        self.title = line.lstrip('#')
        self.level = len(line) - len(self.title)
        self.title = self.title.lstrip()

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        return self.content + '\n'


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

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        return self.content + '\n'


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
        self.level = get_indentation_level(line)

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        return self.content + '\n'


class BlockquoteBlock(Token):
    """Multiple lines of blockquotes.
    
    Attributes
    ----------
    content : List[Blockquote]
        The consecutive blockquote tokens.
    level : int
        The number of spaces of indentation of the first item in the 
        consecutive blockquotes.
    """
    def __init__(self, tokens_: List[Blockquote]):
        self.content = tokens_
        self.level = tokens_[0].level

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        raw_content = [token.raw() for token in self.content]
        return ''.join(raw_content)


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

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        return self.content + '\n'


class ToDo(Token):
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
        self.level = get_indentation_level(line)

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        return self.content + '\n'


class Done(Token):
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
        self.level = get_indentation_level(line)

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        return self.content + '\n'


class ToDoList(Token):
    """A block of ToDo and/or Done tokens.
    
    Attributes
    ----------
    content : List[Union[ToDo, Done]]
        The ToDo token(s) and/or Done token(s).
    level : int
        The number of spaces of indentation of the first item in the 
        list.
    """
    def __init__(self, tokens_: List[Union[ToDo, Done]]):
        self.content = tokens_
        self.level = tokens_[0].level

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        raw_content = [token.raw() for token in self.content]
        return ''.join(raw_content)


class TableRow(Token):
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

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        return self.content + '\n'


class TableDivider(Token):
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

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        return self.content + '\n'


class Table(Token):
    """A table.
    
    Attributes
    ----------
    content : List[Union[TableRow, TableDivider]]
        The table's row token(s) and possibly divider token(s).
    """
    def __init__(self, tokens_: List[Union[TableRow, TableDivider]]):
        self.content = tokens_

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        raw_content = [token.raw() for token in self.content]
        return ''.join(raw_content)


class CodeFence(Token):
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

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        return self.content + '\n'


class CodeBlock(Token):
    """A multi-line code block.
    
    Attributes
    ----------
    content : List[Union[CodeFence, Text]]
        The code block's code fence tokens surrounding text token(s).
    language : str
        Any text that follows the triple backticks (or tildes) on the
        line of the opening code fence. Surrounding whitespace 
        characters are removed.
    """
    def __init__(self, tokens_: List[Union[CodeFence, Text]]):
        self.content = tokens_
        self.language = tokens_[0].language

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        raw_content = [token.raw() for token in self.content]
        return ''.join(raw_content)


class MathFence(Token):
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

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        return self.content + '\n'


class MathBlock(Token):
    """A multi-line mathblock.
    
    Attributes
    ----------
    content : List[Text]
        The mathblock's math fence tokens surrounding text token(s).
    """
    def __init__(self, tokens_: List[Union[MathFence, Text]]):
        self.content = tokens_

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        raw_content = [token.raw() for token in self.content]
        return ''.join(raw_content)


class OrderedListItem(Token):
    """An item in a numbered list.
    
    May contain tags.

    Attributes
    ----------
    content : str
        The content of the line of text.
    level : int
        The number of spaces of indentation.
    pattern : re.Pattern
        The compiled regex pattern for an item in an ordered list. This 
        is a class attribute.
    """
    pattern = patterns.ordered_list_item

    def __init__(self, line: str):
        self.content = line
        self.level = get_indentation_level(line)

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        return self.content + '\n'


class OrderedList(Token):
    """An entire numbered list.
    
    Attributes
    ----------
    content : List[OrderedListItem]
        The tokens that make up the list. Lists may have sublists.
    level : int
        The number of spaces of indentation of the first item in the 
        list.
    """
    def __init__(self, tokens_: List[OrderedListItem] = []):
        self.content = tokens_
        self.level = tokens_[0].level

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        raw_content = [token.raw() for token in self.content]
        return ''.join(raw_content)


class UnorderedListItem(Token):
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
        self.level = get_indentation_level(line)

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        return self.content + '\n'


class UnorderedList(Token):
    """An entire bullet point list.
    
    The list can have bullet points as asterisks, minuses, and/or pluses.

    Attributes
    ----------
    content : List[UnorderedListItem]
        The tokens that make up the list. Lists may have sublists.
    level : int
        The number of spaces of indentation of the first item in the 
        list.
    """
    def __init__(self, tokens_: List[UnorderedListItem] = []):
        self.content = tokens_
        self.level = tokens_[0].level

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        raw_content = [token.raw() for token in self.content]
        return ''.join(raw_content)


class Section(Token):
    """A section of a file, starting with a token of a chosen type.
    
    Section tokens may also contain section tokens in some cases.

    Attributes
    ----------
    content : List[Token]
        The tokens in this section, starting with a token of a chosen 
        type.
    """
    def __init__(self, tokens_: List[Token] = []):
        self.content = tokens_

    def raw(self) -> str:
        """Returns the original content of the token's raw text."""
        raw_content = [token.raw() for token in self.content]
        return ''.join(raw_content)
