import re
from datetime import datetime

class DataValidation:
    """
    A utility class for performing common data validation tasks.
    """

    @staticmethod
    def validate_date(date_string: str, date_format: str = "%Y-%m-%d") -> bool:
        """
        Validates if the provided string is a valid date in the given format.

        Parameters:
            date_string (str): The date string to validate.
            date_format (str): The date format to check against (default: "%Y-%m-%d").

        Returns:
            bool: True if the date is valid, False otherwise.
        """
        try:
            datetime.strptime(date_string, date_format)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validates if the provided string is a valid email address.

        Parameters:
            email (str): The email string to validate.

        Returns:
            bool: True if the email is valid, False otherwise.
        """
        email_regex = '''(^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*
                      @(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)$'''
        if re.match(email_regex, email):
            return True
        return False

    @staticmethod
    def validate_positive_integer(value: str) -> bool:
        """
        Validates if the given string represents a positive integer.

        Parameters:
            value (str): The string to check.

        Returns:
            bool: True if the value is a positive integer, False otherwise.
        """
        return value.isdigit() and int(value) > 0

    @staticmethod
    def validate_non_empty_string(value: str) -> bool:
        """
        Validates if the given string is not empty and does not contain only spaces.

        Parameters:
            value (str): The string to check.

        Returns:
            bool: True if the string is not empty, False otherwise.
        """
        return bool(value and value.strip())

    @staticmethod
    def validate_csv_format(data: list, required_columns: list) -> bool:
        """
        Validates if the given data matches the expected CSV format with the required columns.

        Parameters:
            data (list): A list of dictionaries or lists, each representing a row in the CSV.
            required_columns (list): A list of column names that should exist in the data.

        Returns:
            bool: True if the data has all the required columns, False otherwise.
        """
        if not data:
            return False

        # Check if the first row contains all the required columns
        if set(required_columns).issubset(set(data[0].keys())):
            return True
        return False

    @staticmethod
    def validate_range(value: float, min_value: float, max_value: float) -> bool:
        """
        Validates if the given value is within a specific numeric range.

        Parameters:
            value (float): The value to check.
            min_value (float): The minimum acceptable value.
            max_value (float): The maximum acceptable value.

        Returns:
            bool: True if the value is within the range, False otherwise.
        """
        return min_value <= value <= max_value

    @staticmethod
    def validate_required_fields(data: dict, required_fields: list) -> bool:
        """
        Validates if all required fields are present in the provided data.

        Parameters:
            data (dict): The dictionary containing the data to validate.
            required_fields (list): A list of required field names that should be in the data.

        Returns:
            bool: True if all required fields are present, False otherwise.
        """
        return all(field in data for field in required_fields)

# Example usage:

if __name__ == "__main__":
    # Validate date
    print(DataValidation.validate_date("2024-12-17"))  # True
    print(DataValidation.validate_date("2024-17-12", "%Y-%d-%m"))  # True
    print(DataValidation.validate_date("2024/12/17", "%Y-%m-%d"))  # False

    # Validate email
    print(DataValidation.validate_email("example@domain.com"))  # True
    print(DataValidation.validate_email("invalid-email.com"))  # False

    # Validate positive integer
    print(DataValidation.validate_positive_integer("25"))  # True
    print(DataValidation.validate_positive_integer("-25"))  # False
    print(DataValidation.validate_positive_integer("abc"))  # False

    # Validate non-empty string
    print(DataValidation.validate_non_empty_string("Hello"))  # True
    print(DataValidation.validate_non_empty_string("  "))  # False
    print(DataValidation.validate_non_empty_string(""))  # False

    # Validate CSV format (example)
    sample_data = [
        {"name": "John", "age": "30"},
        {"name": "Jane", "age": "25"}
    ]
    required_columns = ["name", "age"]
    print(DataValidation.validate_csv_format(sample_data, required_columns))  # True

    # Validate range
    print(DataValidation.validate_range(10.5, 5.0, 20.0))  # True
    print(DataValidation.validate_range(3.5, 5.0, 20.0))  # False

    # Validate required fields
    sample_data_dict = {"name": "John", "age": 30}
    required_fields = ["name", "age"]
    print(DataValidation.validate_required_fields(sample_data_dict, required_fields))  # True
