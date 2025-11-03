import pandas as pd
from io import StringIO
from crud import get_connection_pool


class DataDownloader:
    '''
    Class to handle Downloading of the Survey Data as a CSV file.
    '''

    @staticmethod
    def get_data_as_csv():
        """Fetch data from DB and return as CSV string."""
        pg_pool = get_connection_pool()
        conn = pg_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT response_id, " \
                    "h3index, hexdistancetopark, married, municipality, postalcode, education, employment, numkids, age," \
                    "hoursWorked, visitFrequency, wtp, income FROM survey_info"
                )
                rows = cur.fetchall()
                colnames = [desc[0] for desc in cur.description]
                df = pd.DataFrame(rows, columns=colnames)

                csv_buffer = StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
                return csv_buffer.getvalue()
        finally:
            pg_pool.putconn(conn)
