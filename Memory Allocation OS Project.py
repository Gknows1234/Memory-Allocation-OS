class MemoryBlock:
    """Represents a memory block in the memory arena"""
    def __init__(self, offset, size, allocated=False):
        self.offset = offset
        self.size = size
        self.allocated = allocated
        self.next = None
        self.prev = None
    
    def __repr__(self):
        status = "ALLOCATED" if self.allocated else "FREE"
        return f"Block(offset={self.offset}, size={self.size}, {status})"


class MemoryAllocator:
    """Memory allocator supporting multiple allocation policies"""
    
    def __init__(self, total_size, policy="first_fit"):
        """
        Initialize memory allocator
        
        Args:
            total_size: Total memory size in MB
            policy: Allocation policy - "first_fit", "next_fit", "best_fit", or "worst_fit"
        """
        self.total_size = total_size
        self.policy = policy.lower()
        self.next_fit_ptr = None
        
        # Initialize with one large free block
        self.head = MemoryBlock(0, total_size, allocated=False)
        self.next_fit_ptr = self.head
        
        if self.policy not in ["first_fit", "next_fit", "best_fit", "worst_fit"]:
            raise ValueError("Invalid policy. Must be first_fit, next_fit, best_fit, or worst_fit")
    
    def mem_check(self, size):
        """
        Check if memory of requested size is available
        
        Args:
            size: Required memory size in MB
            
        Returns:
            MemoryBlock if available, None otherwise
        """
        if self.policy == "first_fit":
            return self._first_fit(size)
        elif self.policy == "next_fit":
            return self._next_fit(size)
        elif self.policy == "best_fit":
            return self._best_fit(size)
        elif self.policy == "worst_fit":
            return self._worst_fit(size)
    
    def _first_fit(self, size):
        """Find first block that fits"""
        current = self.head
        while current:
            if not current.allocated and current.size >= size:
                return current
            current = current.next
        return None
    
    def _next_fit(self, size):
        """Find next block after last allocation that fits"""
        # Start from next_fit_ptr
        current = self.next_fit_ptr
        start = current
        
        # Search from next_fit_ptr to end
        while current:
            if not current.allocated and current.size >= size:
                self.next_fit_ptr = current
                return current
            current = current.next
        
        # Wrap around and search from beginning to start
        current = self.head
        while current and current != start:
            if not current.allocated and current.size >= size:
                self.next_fit_ptr = current
                return current
            current = current.next
        
        return None
    
    def _best_fit(self, size):
        """Find smallest block that fits"""
        current = self.head
        best_block = None
        best_size = float('inf')
        
        while current:
            if not current.allocated and current.size >= size:
                if current.size < best_size:
                    best_size = current.size
                    best_block = current
            current = current.next
        
        return best_block
    
    def _worst_fit(self, size):
        """Find largest block that fits"""
        current = self.head
        worst_block = None
        worst_size = -1
        
        while current:
            if not current.allocated and current.size >= size:
                if current.size > worst_size:
                    worst_size = current.size
                    worst_block = current
            current = current.next
        
        return worst_block
    
    def mem_split(self, block, size):
        """
        Split a memory block into allocated and free portions
        
        Args:
            block: Block to split
            size: Size to allocate
            
        Returns:
            The allocated block
        """
        if block.size == size:
            # No split needed
            return block
        
        # Create new free block for remaining space
        new_block = MemoryBlock(block.offset + size, block.size - size, allocated=False)
        
        # Update links
        new_block.next = block.next
        new_block.prev = block
        
        if block.next:
            block.next.prev = new_block
        
        block.next = new_block
        block.size = size
        
        return block
    
    def mem_alloc(self, size):
        """
        Allocate memory block
        
        Args:
            size: Size to allocate in MB
            
        Returns:
            Allocated MemoryBlock or None if allocation failed
        """
        # Find suitable block
        block = self.mem_check(size)
        
        if not block:
            return None
        
        # Split if necessary
        if block.size > size:
            block = self.mem_split(block, size)
        
        # Mark as allocated
        block.allocated = True
        
        return block
    
    def mem_merge(self, block):
        """
        Merge adjacent free blocks
        
        Args:
            block: Starting block for merge
            
        Returns:
            Merged block
        """
        # Merge with next block if free
        while block.next and not block.next.allocated:
            next_block = block.next
            block.size += next_block.size
            block.next = next_block.next
            if next_block.next:
                next_block.next.prev = block
        
        # Merge with previous block if free
        while block.prev and not block.prev.allocated:
            prev_block = block.prev
            prev_block.size += block.size
            prev_block.next = block.next
            if block.next:
                block.next.prev = prev_block
            block = prev_block
        
        return block
    
    def mem_free(self, block):
        """
        Free a memory block
        
        Args:
            block: Block to free
            
        Returns:
            The freed (and possibly merged) block
        """
        if not block or not block.allocated:
            return None
        
        # Mark as free
        block.allocated = False
        
        # Merge with adjacent free blocks
        block = self.mem_merge(block)
        
        return block
    
    def print_memory_map(self):
        """Print current memory allocation map"""
        print("\nMemory Map:")
        print(f"{'Offset':<10} {'Size':<10} {'Allocated':<12}")
        print("-" * 35)
        
        current = self.head
        while current:
            status = "TRUE" if current.allocated else "FALSE"
            print(f"{current.offset:<10} {current.size:<10} {status:<12}")
            current = current.next
        
        if self.policy == "next_fit":
            print(f"\nNext Fit Pointer at offset: {self.next_fit_ptr.offset if self.next_fit_ptr else 'None'}")
    
    def get_memory_state(self):
        """Get list of all memory blocks for testing"""
        blocks = []
        current = self.head
        while current:
            blocks.append({
                'offset': current.offset,
                'size': current.size,
                'allocated': current.allocated
            })
            current = current.next
        return blocks


import random


def run_random_simulation(policy):
    """Run simulation with random process sizes"""
    print(f"\n{'='*60}")
    print(f"Random Simulation - {policy.upper().replace('_', ' ')} Policy")
    print(f"{'='*60}")
    
    total_memory = int(input("\nEnter total memory size (MB): "))
    num_processes = int(input("Enter number of processes to generate: "))
    
    allocator = MemoryAllocator(total_memory, policy)
    
    # Generate random processes
    processes = []
    for i in range(num_processes):
        size = random.randint(10, total_memory // 4)
        processes.append((size, f"Process {i}"))
    
    print(f"\nGenerated {num_processes} random processes:")
    for size, name in processes:
        print(f"  {name}: {size} MB")
    
    allocated_blocks = []
    
    print("\n" + "="*60)
    print("Allocating processes:")
    print("="*60)
    for size, name in processes:
        block = allocator.mem_alloc(size)
        if block:
            print(f"✓ {name}: Allocated {size} MB at offset {block.offset}")
            allocated_blocks.append((block, name))
        else:
            print(f"✗ {name}: FAILED to allocate {size} MB (insufficient memory)")
    
    allocator.print_memory_map()
    
    # Ask if user wants to free some processes
    if allocated_blocks:
        print("\n" + "="*60)
        free_choice = input("\nDo you want to free some processes? (y/n): ").lower()
        if free_choice == 'y':
            print("\nCurrently allocated processes:")
            for idx, (block, name) in enumerate(allocated_blocks):
                print(f"  {idx}: {name} - {block.size} MB at offset {block.offset}")
            
            free_indices = input("\nEnter process numbers to free (comma-separated): ")
            try:
                indices = [int(x.strip()) for x in free_indices.split(',')]
                for idx in indices:
                    if 0 <= idx < len(allocated_blocks):
                        block, name = allocated_blocks[idx]
                        allocator.mem_free(block)
                        print(f"  Freed {name}")
                
                allocator.print_memory_map()
            except ValueError:
                print("Invalid input. Skipping free operation.")


def run_user_input_simulation(policy):
    """Run simulation with user-specified process sizes"""
    print(f"\n{'='*60}")
    print(f"User Input Simulation - {policy.upper().replace('_', ' ')} Policy")
    print(f"{'='*60}")
    
    total_memory = int(input("\nEnter total memory size (MB): "))
    allocator = MemoryAllocator(total_memory, policy)
    
    processes = []
    print("\nEnter process sizes (enter 0 or negative to finish):")
    i = 0
    while True:
        try:
            size = int(input(f"  Process {i} size (MB): "))
            if size <= 0:
                break
            processes.append((size, f"Process {i}"))
            i += 1
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    if not processes:
        print("No processes to allocate.")
        return
    
    allocated_blocks = []
    
    print("\n" + "="*60)
    print("Allocating processes:")
    print("="*60)
    for size, name in processes:
        block = allocator.mem_alloc(size)
        if block:
            print(f"✓ {name}: Allocated {size} MB at offset {block.offset}")
            allocated_blocks.append((block, name))
        else:
            print(f"✗ {name}: FAILED to allocate {size} MB (insufficient memory)")
    
    allocator.print_memory_map()
    
    # Interactive menu for operations
    while True:
        print("\n" + "="*60)
        print("Options:")
        print("  1. Allocate another process")
        print("  2. Free a process")
        print("  3. View memory map")
        print("  4. Exit")
        print("="*60)
        
        choice = input("Choose an option: ").strip()
        
        if choice == '1':
            try:
                size = int(input("Enter process size (MB): "))
                name = f"Process {len(processes)}"
                block = allocator.mem_alloc(size)
                if block:
                    print(f"✓ {name}: Allocated {size} MB at offset {block.offset}")
                    allocated_blocks.append((block, name))
                    processes.append((size, name))
                else:
                    print(f"✗ {name}: FAILED to allocate {size} MB (insufficient memory)")
            except ValueError:
                print("Invalid input.")
        
        elif choice == '2':
            if not allocated_blocks:
                print("No allocated processes to free.")
            else:
                print("\nCurrently allocated processes:")
                current_allocated = [(i, b, n) for i, (b, n) in enumerate(allocated_blocks) if b.allocated]
                if not current_allocated:
                    print("No allocated processes to free.")
                else:
                    for idx, block, name in current_allocated:
                        print(f"  {idx}: {name} - {block.size} MB at offset {block.offset}")
                    
                    try:
                        free_idx = int(input("\nEnter process number to free: "))
                        if 0 <= free_idx < len(allocated_blocks):
                            block, name = allocated_blocks[free_idx]
                            if block.allocated:
                                allocator.mem_free(block)
                                print(f"✓ Freed {name}")
                            else:
                                print(f"Process {free_idx} is already freed.")
                        else:
                            print("Invalid process number.")
                    except ValueError:
                        print("Invalid input.")
        
        elif choice == '3':
            allocator.print_memory_map()
        
        elif choice == '4':
            break
        
        else:
            print("Invalid option. Please try again.")


def display_main_menu():
    """Display main menu and handle user choices"""
    while True:
        print("\n" + "="*60)
        print("MEMORY ALLOCATION SIMULATOR")
        print("="*60)
        print("Select Allocation Policy:")
        print("  1. First Fit")
        print("  2. Next Fit")
        print("  3. Best Fit")
        print("  4. Worst Fit")
        print("  5. Exit")
        print("="*60)
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '5':
            print("\nExiting. Goodbye!")
            break
        
        policy_map = {
            '1': 'first_fit',
            '2': 'next_fit',
            '3': 'best_fit',
            '4': 'worst_fit'
        }
        
        if choice not in policy_map:
            print("Invalid choice. Please try again.")
            continue
        
        policy = policy_map[choice]
        
        # Sub-menu for simulation type
        while True:
            print(f"\n{'='*60}")
            print(f"Selected: {policy.upper().replace('_', ' ')} Policy")
            print("="*60)
            print("Select Simulation Type:")
            print("  1. Random processes")
            print("  2. User input processes")
            print("  3. Back to main menu")
            print("="*60)
            
            sub_choice = input("Enter your choice (1-3): ").strip()
            
            if sub_choice == '1':
                run_random_simulation(policy)
            elif sub_choice == '2':
                run_user_input_simulation(policy)
            elif sub_choice == '3':
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    display_main_menu()
