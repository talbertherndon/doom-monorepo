## Setting Up the Project
1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   or freeze
   pip freeze > requirements.txt
   ```bash

   ```

4. Deactivate the virtual environment when done:
   ```bash
   deactivate
   ```

personal access token:
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


go inside the venv folder and find raggraph and replace your create_graph.py file with the one in the rag folder

./venv/lib/python3.10/site-packages/graphrag/index/operations/create_graph.py

also may have issues with rust so just manually install it