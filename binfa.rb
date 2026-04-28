lass Node
  attr_accessor :char, :zero, :one

  def initialize(char = '/')
    @char = char
    @zero = nil
    @one = nil
  end
end

class LZWBinFa
  def initialize
    @root = Node.new
    @current = @root
  end

  def add(bit)
    if bit == '0'
      if @current.zero.nil?
        @current.zero = Node.new('0')
        @current = @root
      else
        @current = @current.zero
      end
    else
      if @current.one.nil?
        @current.one = Node.new('1')
        @current = @root
      else
        @current = @current.one
      end
    end
  end

  def write_tree(out, node = @root, depth = 0)
    return if node.nil?

    write_tree(out, node.one, depth + 1)
    out.puts "#{'---' * depth}#{node.char}(#{depth})"
    write_tree(out, node.zero, depth + 1)
  end

  def get_depth
    @max_depth = 0
    calc_depth(@root, 1)
    @max_depth - 1
  end

  def calc_depth(node, depth)
    return if node.nil?

    @max_depth = depth if depth > @max_depth
    calc_depth(node.one, depth + 1)
    calc_depth(node.zero, depth + 1)
  end

  def get_mean
    @sum_depth = 0
    @count = 0
    calc_mean(@root, 1)
    @count > 0 ? @sum_depth.to_f / @count : 0.0
  end

  def calc_mean(node, depth)
    return if node.nil?

    if node.one.nil? && node.zero.nil?
      @sum_depth += depth
      @count += 1
    end

    calc_mean(node.one, depth + 1)
    calc_mean(node.zero, depth + 1)
  end

  def get_variance
    mean = get_mean
    @variance_sum = 0.0
    @count = 0
    calc_variance(@root, 1, mean)

    if @count > 1
      Math.sqrt(@variance_sum / (@count - 1))
    else
      Math.sqrt(@variance_sum)
    end
  end

  def calc_variance(node, depth, mean)
    return if node.nil?

    if node.one.nil? && node.zero.nil?
      @variance_sum += (depth - mean) ** 2
      @count += 1
    end

    calc_variance(node.one, depth + 1, mean)
    calc_variance(node.zero, depth + 1, mean)
  end
end


def usage
  puts "Usage: ruby lzw.rb input.txt -o output.txt"
end

if ARGV.length != 4 || ARGV[1] != '-o'
  usage
  exit 1
end

input_file = ARGV[0]
output_file = ARGV[3]

tree = LZWBinFa.new

File.open(input_file, 'rb') do |f|
  while (b = f.getbyte)
    break if b == 0x0A
  end

  comment = false

  while (b = f.getbyte)
    if b == 0x3E
      comment = true
      next
    end

    if b == 0x0A
      comment = false
      next
    end

    next if comment || b == 0x4E

    8.times do
      if (b & 0x80) != 0
        tree.add('1')
      else
        tree.add('0')
      end
      b = (b << 1) & 0xFF
    end
  end
end

File.open(output_file, 'w') do |out|
  tree.write_tree(out)
  out.puts "depth = #{tree.get_depth}"
  out.puts "mean = #{tree.get_mean}"
  out.puts "var = #{tree.get_variance}"
end
