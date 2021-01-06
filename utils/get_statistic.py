import sys
import os
import threading
from queue import Queue
from queue import Empty
import get_description


THREADS_NUM = 8


def thread_task(id, xml_files_q, data_q):
    while True:
        try:
            xml_file = xml_files_q.get(False)
            print(xml_files_q.qsize())
        except Empty:
            print("Thread #%i finishes"%id)
            break
        doc_obj_data = get_description.get_documnt_object(xml_file)
        data_q.put(doc_obj_data)
        xml_files_q.task_done()


# Makes simple analysis of tags possible values
def get_statistics(xml_dir):
    # Get names of all xml files from a given directory.
    xml_files = Queue()
    for f in os.listdir(xml_dir):
        if os.path.isfile(os.path.join(xml_dir, f)) and os.path.splitext(f)[-1] == ".xml":
            xml_files.put(os.path.join(xml_dir, f))

    # Queue with Document objects datum.
    data_q = Queue()

    # Parse xml files and get document objects datum.
    for i in range(THREADS_NUM):
        t = threading.Thread(target=thread_task, args=(i, xml_files, data_q))
        t.start()
        t.join()
    xml_files.join()
    print("Done")

    # Use sets to find unique values.
    name = set()
    pose = set()
    truncated = set()
    difficult = set()

    max_num_objects = 0
    while data_q.qsize() != 0:
        objs_in_xml = data_q.get()
        max_num_objects = max(max_num_objects, len(objs_in_xml))
        for i in objs_in_xml:
            name.add(i.name)
            pose.add(i.pose)
            truncated.add(i.truncated)
            difficult.add(i.difficult)

    print("max object number %i" % max_num_objects)
    print("name %s" % name)
    print("pose %s" % pose)
    print("trancated %s" % truncated)
    print("difficult %s" % difficult)


def main():
    # Check command line correctness
    if len(sys.argv) != 2:
        raise "Invalid command line"
    xml_dir = sys.argv[1]
    if not os.path.exists(xml_dir):
        raise "Directory doesn't exist"

    get_statistics(xml_dir)

if __name__ == '__main__':
    main()
