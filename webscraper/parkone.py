import requests
from dotenv import load_dotenv
import os
from urllib.parse import urljoin


class ParkOne:
    def __init__(self):
        load_dotenv()
        self._auth_token = os.getenv("PARKONE_API_TOKEN", "")
        self.headers = {"authorization": self._auth_token}
        self.base_url = "https://api.parkone.dk/v1"
        self.municipality = "vejle"

    def get_by_vehicle(self, license_plate: str):
        """
        Retrieves all the active parkings associated with a specific vehicle for the municipality.
        Parameters:
        license_plate: string

        Response:
        parkingStartTime: string 				(Parking Start At)
        parkingStopAt: string 				(Estimated Parking Stop At)
        vehicleRegId: string 					(Licence Plate Number)
        municipality: string 					(Operator)
        zone: string 						(Zone Name)
        """

        endpoint = "/getActiveParkingsByVehicle"
        url = urljoin(base=self.base_url, url=endpoint)
        params = {"municipality": self.municipality, "vehicleRegId": license_plate}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()


po = ParkOne()
