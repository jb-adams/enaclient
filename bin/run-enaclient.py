from enaclient.enaclient import ENAClient

def main():
    client = ENAClient()
    client.query_ena_all()

if __name__ == "__main__":
    main()
