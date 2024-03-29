from datetime import date
from google.cloud import storage


def write_dataframe_to_gcs(dataframe, bucket_name, file_name):
    # Convert the DataFrame to a CSV string
    csv_data = dataframe.to_csv(index=False)

    # Create a client to interact with the Google Cloud Storage API
    client = storage.Client()

    # Get the bucket object
    bucket = client.get_bucket(bucket_name)

    # Create a blob object with the desired filename
    blob = bucket.blob(file_name)

    # Upload the CSV data to the blob
    blob.upload_from_string(csv_data, 'text/csv')

    print(f"File '{file_name}' uploaded to '{bucket_name}' bucket.")


def format_month(month):
    return str(month) if month > 9 else f"0{month}"


def compute_last_year_month():
    current_date = date.today()
    if current_date.month == 1:
        year = current_date.year - 1
        month = 12
    else:
        year = current_date.year
        month = current_date.month - 1

    return year, month
