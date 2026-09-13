import requests
import streamlit as st
from typing import Dict, Any, List, Optional
from config import API_BASE_URL

REQUEST_TIMEOUT = 6.0

class APIClientError(Exception):
    """Base exception for dashboard API interactions."""
    pass

@st.cache_data(ttl=60)
def fetch_trend() -> List[Dict[str, Any]]:
    """Fetch 30-day APIx index values."""
    url = f"{API_BASE_URL}/trend"
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            raise APIClientError("Unexpected format from /trend endpoint.")
        return data
    except requests.exceptions.ConnectionError:
        raise APIClientError("Backend analytics service is currently unavailable. Please verify API service connectivity.")
    except requests.exceptions.Timeout:
        raise APIClientError("Analytics service request timed out.")
    except Exception as e:
        raise APIClientError(f"Unable to load APIx trend: {type(e).__name__}")


@st.cache_data(ttl=60)
def fetch_heatmap(metric: str = "index", routes: Optional[List[str]] = None, windows: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Fetch Route Heatmap matrix for price index or fares."""
    url = f"{API_BASE_URL}/route-heatmap"
    params = {"metric": metric}
    if routes:
        params["routes"] = ",".join(routes)
    if windows:
        params["windows"] = ",".join(windows)

    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            raise APIClientError("Unexpected format from /route-heatmap.")
        return data
    except requests.exceptions.ConnectionError:
        raise APIClientError("Backend server connection failed for Route Heatmap.")
    except Exception as e:
        raise APIClientError(f"Failed to load Route Heatmap: {e}")

@st.cache_data(ttl=60)
def fetch_lead_time_curve(route: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch lead-time representative fare curve."""
    url = f"{API_BASE_URL}/elasticity"
    params = {}
    if route and route != "All Routes":
        params["route"] = route

    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            raise APIClientError("Unexpected format from /elasticity.")
        return data
    except Exception as e:
        raise APIClientError(f"Failed to load Lead-Time Fare Curve: {e}")

@st.cache_data(ttl=60)
def fetch_airline_comparison(route: Optional[str] = None, window: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch airline representative fare comparison."""
    url = f"{API_BASE_URL}/airline-comparison"
    params = {}
    if route and route != "All Routes":
        params["route"] = route
    if window and window != "All Windows":
        params["window"] = window

    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            raise APIClientError("Unexpected format from /airline-comparison.")
        return data
    except Exception as e:
        raise APIClientError(f"Failed to load Airline Comparison: {e}")

@st.cache_data(ttl=60)
def fetch_contributors() -> Dict[str, Any]:
    """Fetch index change breakdown by route."""
    url = f"{API_BASE_URL}/index-contributors"
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise APIClientError(f"Failed to load Contributor Analysis: {e}")

@st.cache_data(ttl=60)
def fetch_benchmark() -> Dict[str, Any]:
    """Fetch DGCA benchmark validation comparison."""
    url = f"{API_BASE_URL}/benchmark"
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise APIClientError(f"Failed to load DGCA Benchmark: {e}")

@st.cache_data(ttl=60)
def fetch_data_quality() -> Dict[str, Any]:
    """Fetch data audit, validity, and coverage metrics."""
    url = f"{API_BASE_URL}/data-quality"
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise APIClientError(f"Failed to load Data Quality metrics: {e}")
