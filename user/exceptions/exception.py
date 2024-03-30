class MissingRequiredFields(Exception):
    def __init__(self, fields):
        super().__init__(f"Missing required fields: {fields}")
        self.code = "MissingRequiredFields"
        self.message = f"Missing required fields: {fields}"
        self.fields = fields
