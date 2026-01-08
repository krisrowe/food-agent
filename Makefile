.PHONY: install clean register

install:
	@echo "Installing food-agent in editable mode via pipx..."
	pipx install -e . --force

register:
	@echo "Registering food-agent with Gemini CLI..."
	# We use the installed 'food-agent' command
	gemini mcp add food-agent food-agent --stdio

clean:
	rm -rf build dist *.egg-info
	find . -name "__pycache__" -type d -exec rm -rf {} +
