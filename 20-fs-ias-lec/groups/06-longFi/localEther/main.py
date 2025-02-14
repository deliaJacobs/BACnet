import os
import pcap
from logSync import pcap_sync
from logSync import database_sync
import udp_connection


def check_dir(dir1):
    print(dir1)
    if not os.path.isdir(dir1):
        print("Directories do not exist")
        sys.exit()


def sync_directories(dir_list):
    check_dir(dir_list)
    dir1 = dir_list[0]
    dir2 = dir_list[1]
    list1 = pcap_sync.create_list_of_files(dir1)
    list2 = pcap_sync.create_list_of_files(dir2)

    print("sync...")

    new_file_list1 = []
    for i in list1:
        found = False
        for j in list2:
            file1, key1 = i[:2]
            file2, key2 = j[:2]
            if key1 == key2:
                found = True
                synchro = pcap_sync.Sync(dir1 + file1, dir2 + file2)
                # Only syncs if files are not up-to-date
                if not synchro.up_to_date:
                    synchro.sync_files()
                # Pops element of the second list if match was found to avoid unnecessary iterations
                list2.pop(list2.index(j))
                continue
        # If no match was found for the element of the first list, that means that the file is new and needs to be
        # added to the second list, respectively second directory. This is done below.
        if not found:
            new_file_list1.append(i)

    list1 = new_file_list1
    print(list1)
    print(list2)

    if list1:
        for i in list1:
            file, key = i[:2]
            synchro = pcap_sync.Sync(dir1 + file, dir2 + file)
            synchro.sync_files(True, key)

    if list2:
        for i in list2:
            file, key = i[:2]
            synchro = pcap_sync.Sync(dir1 + file, dir2 + file)
            synchro.sync_files(True, key)


def dump_directories_cont(dir1):
    check_dir(dir1)
    list1 = pcap_sync.create_list_of_files(dir1)
    for i in list1:
        print(dir1 + i[0] + ':')
        pcap.dump(dir1 + i[0])
        print("-------------------------------")


if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Tool for synchronisation')

    parser.add_argument('--sync', metavar='DIR', nargs=2)
    parser.add_argument('--dump', metavar='DIR')
    parser.add_argument('--hasPackets', metavar='hasPackets', nargs=1)
    parser.add_argument('--needsPackets', metavar='needsPackets', nargs=1)
    args = parser.parse_args()

    if args.dump is not None:
        dump_directories_cont(args.dump)

    if args.sync is not None:
        sync_directories(args.sync)

    if args.hasPackets is not None:
        hasPackets = udp_connection.hasPackets(args.hasPackets[0])
        # print(server.get_packet_to_send_as_bytes())

    if args.needsPackets is not None:
        needsPackets = udp_connection.needsPackets(args.needsPackets[0])
        # print(client.get_packet_to_receive_as_bytes())

        # This is the crucial function for the other groups (Synchronisation). The client contains two important lists:
        # A list of files that are going to be extended and their corresponding extensions (groups will enter their
        # received packets instead of client.get_packet_to_receive_as_bytes())

        # sync.sync_database(client.get_list_of_needed_extensions(), client.get_packet_to_receive_as_bytes())
        database_sync.sync_database(needsPackets.get_list_of_needed_extensions(),
                                    needsPackets.get_packet_to_receive_as_bytes())
