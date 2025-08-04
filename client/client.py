from client_core import simulate_ransomware, simulate_recovery
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ransomware Simulation Client')
    parser.add_argument('--attack', action='store_true', help='Run ransomware simulation')
    parser.add_argument('--recover', metavar='CLIENT_ID', help='Client ID for recovery')
    parser.add_argument('--token', help='Admin token for recovery')
    
    args = parser.parse_args()
    
    if args.attack:
        simulate_ransomware()
    elif args.recover and args.token:
        simulate_recovery(args.recover, args.token)
    else:
        print("Invalid command. Use --attack or --recover with --token")