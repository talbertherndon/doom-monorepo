graph rag your doom scrolling

graphrag is the future<img width="1710" height="1107" alt="Screenshot 2025-03-18 at 1 21 39 PM" src="https://github.com/user-attachments/assets/4f1e5a73-8331-4c16-85ae-da3e61f3e0f6" />

<img width="1403" height="911" alt="Screenshot 2025-03-24 at 5 03 09 PM" src="https://github.com/user-attachments/assets/3c884664-cb4d-4f23-ac3d-aaddeb0c1246" />


<img width="1692" height="921" alt="Screenshot 2025-03-24 at 4 31 17 PM" src="https://github.com/user-attachments/assets/ac527538-92af-4db6-a5f5-2b7220dc5e05" />


go to root folder and run:

graphrag index --root ./ragtest --config ./ragtest/settings.yaml


then once that is done, run:

python graphml_to_json.py


run the react app:

cd doom-or-boom
npm install
npm start



also query the graph:
    ragtest graphrag query \
    --root ./ragtest \
    --method global \
    --query "What are the top themes in this story?"







