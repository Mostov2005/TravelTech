import os

import grpc
from fastapi import HTTPException

import flight_pb2
import flight_pb2_grpc


FLIGHT_SERVICE_ADDRESS = os.getenv(
    "FLIGHT_SERVICE_ADDRESS",
    "localhost:50051"
)


def get_flight(flight_id: str):
    try:
        with grpc.insecure_channel(FLIGHT_SERVICE_ADDRESS) as channel:
            stub = flight_pb2_grpc.FlightServiceStub(channel)

            response = stub.GetFlight(
                flight_pb2.GetFlightRequest(flight_id=flight_id),
                timeout=5
            )

            return response

    except grpc.RpcError as error:
        if error.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=404,
                detail="Flight not found"
            )

        if error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(
                status_code=400,
                detail="Invalid flight ID"
            )

        raise HTTPException(
            status_code=503,
            detail="Flight Service is unavailable"
        )
