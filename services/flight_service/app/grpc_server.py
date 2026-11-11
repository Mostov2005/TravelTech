from concurrent import futures
from uuid import UUID
from datetime import timezone

import grpc

import flight_pb2
import flight_pb2_grpc
from database import SessionLocal
from services import FlightService


class FlightServicer(flight_pb2_grpc.FlightServiceServicer):

    def GetFlight(self, request, context):
        db = SessionLocal()

        try:
            flight = FlightService(db).get_flight(UUID(request.flight_id))

            return flight_pb2.FlightResponse(
                id=str(flight.id),
                flight_number=flight.flight_number,
                airline=flight.airline,
                departure_airport=flight.departure_airport.iata_code,
                arrival_airport=flight.arrival_airport.iata_code,
                departure_time=flight.departure_time.isoformat(),
                arrival_time=flight.arrival_time.isoformat()
            )

        except ValueError:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Invalid flight ID"
            )

        except Exception as error:
            if getattr(error, "status_code", None) == 404:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Flight not found"
                )
            context.abort(
                grpc.StatusCode.INTERNAL,
                str(error)
            )

        finally:
            db.close()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    flight_pb2_grpc.add_FlightServiceServicer_to_server(
        FlightServicer(),
        server
    )

    server.add_insecure_port("[::]:50051")
    server.start()

    print("Flight gRPC server started on port 50051")

    server.wait_for_termination()
