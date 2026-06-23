
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
    Curator=101
    Leader=100
    Agent=102