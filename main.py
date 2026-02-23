from controllers.ingress_controller import IngressController
from controllers.sentiment_controller import SentimentController
from controllers.core_controller import CoreController
from controllers.egress_controller import EgressController
from config import settings

if __name__ == "__main__":
    ingress = IngressController()
    sentiment = SentimentController()
    core = CoreController()
    egress = EgressController()
    
    ingress.run()
    sentiment.run()
    core.run()
    egress.run(settings.CHOICE_THREE)
