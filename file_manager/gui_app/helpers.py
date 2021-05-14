import os


def path_is_parent(parent_path, child_path):
    parent_path = os.path.abspath(parent_path)
    child_path = os.path.abspath(child_path)
    return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])

def rewrite_tf(tf, s, disabled=True):
    """Rewritest text field"""
    tf.configure(state='normal')
    tf.delete('1.0', 'end')
    tf.insert('end', s)
    if disabled:
        tf.configure(state='disabled')

def shorten_path(path, max_len=45):
    """Shortens path if len(path) > max_len"""
    if len(path) <= max_len:
        return path
    parts = os.path.normpath(path).split(os.sep)
    if len(parts) < 3:
        return path
    beginning = []
    end = []
    counter = 3
    bc = 0
    ec = len(parts) - 1
    while True:
        bp = parts[bc]
        bc += 1
        counter += len(bp) + 1
        if counter >= max_len:
            break
        beginning.append(bp)

        ep = parts[ec]
        ec -= 1
        counter += len(ep) + 1
        if counter >= max_len:
            break
        end.insert(0, ep)

        if ec -bc <= 3:
            break

    beginning.extend(['...', *end])
    return '/'.join(beginning)


    