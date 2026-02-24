from pipelines.ingress_pipeline import IngressPipeline
from pipelines.sentiment_pipeline import SentimentPipeline
from pipelines.core_pipeline import CorePipeline
from pipelines.egress_pipeline import EgressPipeline
from settings import settings

if __name__ == "__main__":
    ingress = IngressPipeline()
    sentiment = SentimentPipeline()
    core = CorePipeline()
    egress = EgressPipeline()

    ingress.run()
    sentiment.run()
    core.run()
    egress.run(settings.CHOICE_THREE)
