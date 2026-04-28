import math
import sys


class Node:
    def __init__(self, char='/'):
        self.char = char
        self.zero = None
        self.one = None


class LZWBinFa:
    def __init__(self):
        self.root = Node()
        self.current = self.root

    def add(self, bit):
        if bit == '0':
            if self.current.zero is None:
                self.current.zero = Node('0')
                self.current = self.root
            else:
                self.current = self.current.zero
        else:
            if self.current.one is None:
                self.current.one = Node('1')
                self.current = self.root
            else:
                self.current = self.current.one

    def write_tree(self, out, node=None, depth=0):
        if node is None:
            node = self.root

        if node is None:
            return

        self.write_tree(out, node.one, depth + 1)
        out.write(f"{'---' * depth}{node.char}({depth})\n")
        self.write_tree(out, node.zero, depth + 1)

    def get_depth(self):
        self.max_depth = 0
        self._calc_depth(self.root, 1)
        return self.max_depth - 1

    def _calc_depth(self, node, depth):
        if node is None:
            return

        if depth > self.max_depth:
            self.max_depth = depth

        self._calc_depth(node.one, depth + 1)
        self._calc_depth(node.zero, depth + 1)

    def get_mean(self):
        self.sum_depth = 0
        self.count = 0
        self._calc_mean(self.root, 1)
        return self.sum_depth / self.count if self.count else 0.0

    def _calc_mean(self, node, depth):
        if node is None:
            return

        if node.one is None and node.zero is None:
            self.sum_depth += depth
            self.count += 1

        self._calc_mean(node.one, depth + 1)
        self._calc_mean(node.zero, depth + 1)

    def get_variance(self):
        mean = self.get_mean()
        self.variance_sum = 0.0
        self.count = 0
        self._calc_variance(self.root, 1, mean)

        if self.count > 1:
            return math.sqrt(self.variance_sum / (self.count - 1))

        return math.sqrt(self.variance_sum)

    def _calc_variance(self, node, depth, mean):
        if node is None:
            return

        if node.one is None and node.zero is None:
            self.variance_sum += (depth - mean) ** 2
            self.count += 1

        self._calc_variance(node.one, depth + 1, mean)
        self._calc_variance(node.zero, depth + 1, mean)


def usage():
    print("Usage: python lzw.py input.txt -o output.txt")


def main():
    if len(sys.argv) != 4 or sys.argv[2] != "-o":
        usage()
        return

    input_file = sys.argv[1]
    output_file = sys.argv[3]

    tree = LZWBinFa()

    with open(input_file, "rb") as f:
        while True:
            b = f.read(1)
            if not b or b == b'\n':
                break

        comment = False

        while True:
            b = f.read(1)
            if not b:
                break

            byte = b[0]

            if byte == 0x3E:  # '>'
                comment = True
                continue

            if byte == 0x0A:  # newline
                comment = False
                continue

            if comment or byte == 0x4E:  # 'N'
                continue

            for _ in range(8):
                if byte & 0x80:
                    tree.add('1')
                else:
                    tree.add('0')
                byte = (byte << 1) & 0xFF

    with open(output_file, "w", encoding="utf-8") as out:
        tree.write_tree(out)
        out.write(f"depth = {tree.get_depth()}\n")
        out.write(f"mean = {tree.get_mean()}\n")
        out.write(f"var = {tree.get_variance()}\n")


if __name__ == "__main__":
    main()
