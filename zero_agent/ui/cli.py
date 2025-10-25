"""
Command-line interface for Zero Agent
Simple REPL for interacting with the agent
"""

import asyncio
from colorama import init, Fore, Style
from zero_agent.core.orchestrator import ZeroOrchestrator


# Initialize colorama for Windows - temporarily disabled due to encoding issues
# init(autoreset=True)


class CLI:
    """Command-line interface for Zero Agent"""
    
    def __init__(self, orchestrator: ZeroOrchestrator):
        self.orchestrator = orchestrator
        self.running = True
    
    def print_banner(self):
        """Print welcome banner"""
        banner = f"""
{'='*60}
  ######  ###### #####   ####      ##   ##### ###### #   # #####
     ##   ##     ##  ## ##  ##    #  #  ##    ##     ##  #   ##
    ##    #####  #####  ##  ##   ######  ## ## #####  ####    ##
   ##     ##     ##  ## ##  ##  ##    ## ##  # ##     ##  #   ##
  ######  ###### ##  ##  ####  ##      # ##### ###### ##  #   ##

{'='*60}
Zero Agent v0.1.0 - AI-Powered Autonomous Agent
Type 'help' for commands, 'exit' to quit
{'='*60}
"""
        print(banner)
    
    def print_help(self):
        """Print help message"""
        help_text = f"""
Available Commands:
Natural Language Tasks:  Just type what you want Zero to do!
  
  Examples:
  - "zero search the web for Python tutorials"
  - "zero take a screenshot"
  - "zero check memory usage"
  - "zero create a git repo called test-project"

Special Commands:  help    - Show this help message
  status  - Show system status
  stats   - Show memory statistics
  tools   - List available tools
  clear   - Clear screen
  exit    - Exit Zero Agent

Tip: Be specific in your requests for best results!"""
        print(help_text)
    
    def print_status(self):
        """Print system status"""
        print(f"\nSystem Status:")
        print(f"  Models: {len(self.orchestrator.model_router.list_available_models())} available")
        print(f"  Tools: {len(self.orchestrator.tool_executor.list_tools())} available")
        
        stats = self.orchestrator.rag_system.get_stats()
        print(f"\nMemory Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print()
    
    def print_tools(self):
        """Print available tools"""
        tools = self.orchestrator.tool_executor.list_tools()
        print(f"\nAvailable Tools ({len(tools)}):")
        for tool in tools:
            print(f"  - {tool}")
        print()
    
    async def process_command(self, command: str):
        """Process user command"""
        command = command.strip()
        
        if not command:
            return
        
        # Special commands
        if command.lower() == "exit":
            self.running = False
            print(f"Goodbye!")
            return
        
        elif command.lower() == "help":
            self.print_help()
            return
        
        elif command.lower() == "status":
            self.print_status()
            return
        
        elif command.lower() == "stats":
            stats = self.orchestrator.rag_system.get_stats()
            print(f"\nMemory Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            print()
            return
        
        elif command.lower() == "tools":
            self.print_tools()
            return
        
        elif command.lower() == "clear":
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            self.print_banner()
            return
        
        # Regular task
        print(f"\n[ZERO] Processing your request...\n")
        
        try:
            result = await self.orchestrator.run(command)
            
            # Print results
            print(f"\n{'='*60}")
            print(f"[OK] Task Complete")
            print(f"{'='*60}\n")
            
            if result.get("final_response"):
                print(result["final_response"])
            
            # Show tool results if available
            if result.get("tool_results"):
                print(f"\n[DETAILS] Execution Details:")
                for step_idx, step_result in result["tool_results"].items():
                    print(f"\n  Step {step_idx + 1}: {step_result.get('step', 'Unknown')}")
                    if "tool" in step_result:
                        print(f"    Tool: {step_result['tool']}")
                    if "result" in step_result:
                        res = step_result["result"]
                        if isinstance(res, dict):
                            if res.get("success"):
                                print(f"    [OK] Success")
                            else:
                                print(f"    [FAIL] Failed: {res.get('error', 'Unknown')}")
            
            print(f"\n{'='*60}\n")
            
        except Exception as e:
            print(f"\n[ERROR] Error: {e}\n")
    
    async def run(self):
        """Run the CLI loop"""
        self.print_banner()
        print("Type 'help' for commands or just describe what you want Zero to do.")

        while self.running:
            try:
                # Get input
                prompt = f"Zero $ "
                command = input(prompt)

                # Process command
                await self.process_command(command)
                
            except KeyboardInterrupt:
                print(f"\nUse 'exit' to quit")
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        # Cleanup
        await self.orchestrator.tool_executor.cleanup()

