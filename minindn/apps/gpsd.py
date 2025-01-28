# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2025, The University of Memphis,
#                          Arizona Board of Regents,
#                          Regents of the University of California.
#
# This file is part of Mini-NDN.
# See AUTHORS.md for a complete list of Mini-NDN authors and contributors.
#
# Mini-NDN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mini-NDN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mini-NDN, e.g., in COPYING.md file.
# If not, see <http://www.gnu.org/licenses/>.

import threading
import math
import time
import datetime
from typing import Optional, Tuple

from minindn.apps.application import Application


class Gpsd(Application):
    """
    A class that simulates a GPS device and provides GPS data in NMEA format.
    This class can generate NMEA GGA and VTG sentences and feeds the GPS data to a GPSD server.

    To use this class, you need to install gpsd and netcat (nc) for communication.
    """

    def __init__(self, node, lat: float = 0.0, lon: float = 0.0, altitude: float = 0.0, update_interval: float = 0.2) -> None:
        """
        Initialize the GPSd application for a node.

        :param node: The node for which the GPS data will be provided.
        :param lat: Latitude of the point (0, 0, 0).
        :param lon: Longitude of the point (0, 0, 0).
        :param altitude: Altitude of the point (0, 0, 0).
        :param update_interval: The time interval in seconds to send gps data to gpsd, and it should be more than 0.2
        """
        Application.__init__(self, node)
        self.lat = lat
        self.lon = lon
        self.altitude = altitude
        self.update_interval = update_interval
        self.stop_event = threading.Event()
        self.location_thread = None


    def calculate_coordinates(self, offset_lat: float, offset_lon: float, altitude_offset: float) -> Tuple[float, float, float]:
        """
        Calculate the coordinates of the target point.

        :param offset_lat: Latitude offset (unit: meters)
        :param offset_lon: Longitude offset (unit: meters)
        :param altitude_offset: Altitude offset (unit: meters)
        :return: New GPS coordinates (latitude, longitude, altitude)
        """
        # Each degree of latitude is approximately 111 kilometers
        lat_offset_deg = offset_lat / 111000.0  # Convert to degrees
        # Distance per degree of longitude changes based on latitude
        lon_offset_deg = offset_lon / (111000.0 * math.cos(math.radians(self.lat)))  # Convert to degrees
        # Calculate the latitude, longitude, and altitude of the target point
        lat2 = self.lat + lat_offset_deg
        lon2 = self.lon + lon_offset_deg
        alt2 = self.altitude + altitude_offset

        return lat2, lon2, alt2

    @staticmethod
    def nmea_checksum(sentence: str) -> str:
        """
        Calculate the checksum for an NMEA sentence.
        :param sentence: The NMEA sentence to calculate the checksum for.
        :return: The checksum for the sentence.
        """
        checksum = 0
        for char in sentence:
            checksum ^= ord(char)
        return f"{checksum:02X}"

    @staticmethod
    def generate_vtg_sentence(vx: float, vy: float) -> str:
        """
        Generate a NMEA VTG sentence based on a 2D velocity vector.

        Parameters:
            vx (float): Velocity in the x-direction (eastward, in m/s)
            vy (float): Velocity in the y-direction (northward, in m/s)

        Returns:
            str: The corresponding NMEA VTG sentence
        """
        # Calculate ground speed (horizontal speed)
        ground_speed = math.sqrt(vx**2 + vy**2)  # Ground speed in m/s
        ground_speed_knots = ground_speed * 1.94384  # Convert speed to knots
        ground_speed_kmh = ground_speed * 3.6       # Convert speed to km/h
        # Calculate heading angle (relative to true north, clockwise)
        angle = math.atan2(vx, vy)  # atan2(y, x)
        true_course = (math.degrees(angle) + 360) % 360  # Normalize angle to 0° - 360°
        # Create the VTG NMEA sentence
        nmea_sentence = f"GPVTG,{true_course:.1f},T,,M,{ground_speed_knots:.2f},N,{ground_speed_kmh:.2f},K"

        nmea_sentence_with_checksum = f"${nmea_sentence}*{Gpsd.nmea_checksum(nmea_sentence)}"

        return nmea_sentence_with_checksum

    @staticmethod
    def generate_gga_sentence(lat: float, lon: float, altitude: float, utc_time: Optional[str] = None) -> str:
        """
        Convert latitude, longitude, and altitude into NMEA format data.

        Parameters:
        lat (float): Latitude (unit: degrees)
        lon (float): Longitude (unit: degrees)
        altitude (float): Altitude (unit: meters)
        utc_time (str): UTC Time in 'hhmmss.sss' format, optional

        Returns:
        str: Formatted NMEA data sentence
        """
        lat_direction = 'N' if lat >= 0 else 'S'
        lon_direction = 'E' if lon >= 0 else 'W'

        lat_deg = int(abs(lat))
        lat_min = (abs(lat) - lat_deg) * 60
        lon_deg = int(abs(lon))
        lon_min = (abs(lon) - lon_deg) * 60

        if utc_time is None:
            utc_time = datetime.datetime.now(datetime.timezone.utc).strftime("%H%M%S.%f")[:-3]# Generate UTC time

        nmea_sentence = f"GPGGA,{utc_time},{lat_deg:02d}{lat_min:07.4f},{lat_direction},{lon_deg:03d}{lon_min:07.4f},{lon_direction},1,12,1.0,{altitude:.1f},M,0.0,M,,"

        nmea_sentence = f"${nmea_sentence}*{Gpsd.nmea_checksum(nmea_sentence)}"

        return nmea_sentence

    @staticmethod
    def generate_rmc_sentence(lat: float, lon: float, vx: float, vy: float, utc_time: Optional[str] = None, date: Optional[str] = None) -> str:
        """
        Generate an NMEA GPRMC sentence using vx and vy (speed components along X and Y axes).

        Parameters:
        lat (float): Latitude (degrees)
        lon (float): Longitude (degrees)
        vx (float): Speed along the X-axis (knots)
        vy (float): Speed along the Y-axis (knots)
        utc_time (str, optional): UTC time in 'hhmmss.sss' format
        date (str, optional): UTC date in 'ddmmyy' format

        Returns:
        str: Formatted NMEA GPRMC sentence
        """
        # Calculate speed and course
        speed = math.sqrt(vx**2 + vy**2)  # Speed (ground speed)
        course = math.degrees(math.atan2(vy, vx))  # Course (direction in degrees)

        # Normalize course to be within 0 to 360 degrees
        if course < 0:
            course += 360

        # Convert latitude and longitude to NMEA format
        lat_direction = 'N' if lat >= 0 else 'S'
        lon_direction = 'E' if lon >= 0 else 'W'

        lat_deg = int(abs(lat))
        lat_min = (abs(lat) - lat_deg) * 60
        lon_deg = int(abs(lon))
        lon_min = (abs(lon) - lon_deg) * 60

        # Use current utc_time and date if not provided
        if utc_time is None or date is None:
            now = datetime.datetime.now(datetime.timezone.utc)
            if utc_time is None:
                utc_time = now.strftime("%H%M%S.%f")[:-3]  # hhmmss.sss
            if date is None:
                date = now.strftime("%d%m%y")  # ddmmyy

        # Construct NMEA sentence
        status = "A"  # A = Active, V = Void (No fix)
        nmea_sentence = f"GPRMC,{utc_time},{status},{lat_deg:02d}{lat_min:07.4f},{lat_direction},{lon_deg:03d}{lon_min:07.4f},{lon_direction},{speed:.1f},{course:.1f},{date},,,A"

        nmea_sentence = f"${nmea_sentence}*{Gpsd.nmea_checksum(nmea_sentence)}"

        return nmea_sentence

    def __feedGPStoGPSD(self, node) -> None:
        """
        Continuously feed GPS data to the GPSD server.
        """
        current_position = node.position
        current_time_seconds = time.monotonic()
        while not self.stop_event.is_set():
            time.sleep(self.update_interval)
            lat, lon, altitude = self.calculate_coordinates(node.position[0], node.position[1], node.position[2])
            gga_sentence = self.generate_gga_sentence(lat, lon, altitude)

            tmp_position = node.position
            tmp_time_seconds = time.monotonic()
            vx = (tmp_position[0] - current_position[0]) / (tmp_time_seconds - current_time_seconds)
            vy = (tmp_position[1] - current_position[1]) / (tmp_time_seconds - current_time_seconds)
            current_position = tmp_position
            current_time_seconds = tmp_time_seconds
            rmc_sentence = self.generate_rmc_sentence(lat, lon, vx, vy)
            vtg_sentence = self.generate_vtg_sentence(vx, vy)

            cmd = f"echo '{gga_sentence}\n{rmc_sentence}\n{vtg_sentence}\n' | nc -u -w 1 127.0.0.1 7150"
            process = node.popen(cmd, shell=True)

    def start(self) -> None:
        """
        Start a thread to periodically send GPS data for the node.
        """
        Application.start(self, command="gpsd -n udp://127.0.0.1:7150")

        self.location_thread = threading.Thread(target=self.__feedGPStoGPSD, args=(self.node,))
        self.location_thread.start()

    def stop(self) -> None:
        """
        Stop all the __feedGPStoGPSD threads
        """
        if not self.stop_event.is_set():
            self.stop_event.set()
        self.location_thread.join()
        Application.stop(self)