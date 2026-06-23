
class AdministratorsRank:
    """
    Administrator titles
    
    attributes:
    
    - Agent
    - Leader
    - Curator

    """
    Agent: str = "agent"
    Leader: str = "leader"
    Curator: str = "curator"

    all: tuple = (Agent, Leader, Curator)



class AltAminoAdminRank:
    Curator=100
    Leader=101
    Agent=102