import boto3

class S3Client:
    def __init__(self):
        self.bucket_name = 'prism-bi'
        self.cache_ttl = 60 * 60 * 24 # 1 day
        self.s3 = boto3.client('s3')

    def get_object(self, object_key):
        """
        Gets an object from S3.

        Args:
            object_key (str): The key of the object in the S3 bucket.

        Returns:
            bytes: The contents of the object.
        """
        print("Fetching object from S3...")
        response = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
        return response['Body'].read()

    def put_object(self, object_key, body):
        """
        Puts an object into S3.

        Args:
            object_key (str): The key of the object in the S3 bucket.
            body (bytes): The contents of the object.
        """

        self.s3.put_object(Bucket=self.bucket_name, Key=object_key, Body=body)

    def delete_object(self, object_key):
        """
        Deletes an object from S3.

        Args:
            object_key (str): The key of the object in the S3 bucket.
        """

        self.s3.delete_object(Bucket=self.bucket_name, Key=object_key)

