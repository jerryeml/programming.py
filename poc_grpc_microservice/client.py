import grpc
from poc_grpc_microservice.recommendations.recommendations_pb2_grpc import RecommendationsStub
from poc_grpc_microservice.recommendations.recommendations_pb2 import BookCategory, RecommendationRequest


request = RecommendationRequest(user_id=1, 
                                category=BookCategory.SCIENCE_FICTION,
                                max_results=1)


print(request.max_results)


channel = grpc.insecure_channel("localhost:50051")
client = RecommendationsStub(channel)
print(client.Recommend(request))
