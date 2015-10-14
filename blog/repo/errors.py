__author__ = 'tyerq'


class RepoError(Exception):
    """
    Base class for repository exceptions
    """


class EntryExists(RepoError):
    """
    Entry with same id already exists in database
    """


class EntryNotFound(RepoError):
    """
    "Entry not found in database" error
    """


class WrongCredentials(RepoError):
    """
    Wrong login or password
    """


class SomethingWentWrong(RepoError):
    """
    General "something went wrong" error
    """
    def __init__(self, error):
        """
        initialise SomethingWentWrong with the error it was raised because of

        :param error:Exception
        """

        self.err = error

    def __str__(self):
        return self.err.__str__()


class WrongDocumentStructure(RepoError):
    """
    Something wrong with the schema
    """