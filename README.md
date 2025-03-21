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







