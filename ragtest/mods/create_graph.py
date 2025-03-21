# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing create_graph definition."""

import networkx as nx
import pandas as pd


def create_graph(edges_df: pd.DataFrame) -> nx.Graph:
    """Create a networkx graph from nodes and edges, enriching with metadata."""

    # Step 1: Load metadata from input.parquet
    metadata_file = "./ragtest/output/input.parquet"
    metadata_df = pd.read_parquet(metadata_file)
    metadata_df = metadata_df.rename(columns={"source": "url"})

    # Step 2: Load base_text_units (contains mapping of id → document_ids)
    base_text_units_file = "./ragtest/output/create_base_text_units.parquet"
    base_text_units = pd.read_parquet(base_text_units_file)

    # Debugging: Check column names
    print("metadata_df columns:", metadata_df.columns)
    print("base_text_units columns:", base_text_units.columns)
    print("edges_df columns:", edges_df.columns)

    # Ensure metadata_df has 'id' column
    if "id" not in metadata_df.columns:
        raise KeyError("Column 'id' not found in metadata_df!")

    # Ensure base_text_units has 'id' column
    if "id" not in base_text_units.columns:
        raise KeyError("Column 'id' not found in base_text_units!")

    # Step 3: Explode document_ids so each document_id gets its own row
    base_text_units_exploded = base_text_units.explode("document_ids")

    # Step 4: Merge base_text_units_exploded with metadata (map document_ids → metadata)
    merged_df = base_text_units_exploded.merge(
        metadata_df,
        left_on="document_ids",  # Match document_ids with metadata's id
        right_on="id",
        how="left"
    )

    # Ensure "id" is not dropped if it's needed
    if "id" in merged_df.columns:
        merged_df = merged_df.drop(columns=["id"])  # Drop redundant id column from metadata_df

    # Step 5: Explode text_unit_ids in edges_df (to match with base_text_units.id)
    edges_df_exploded = edges_df.explode("text_unit_ids")

    # Step 6: Merge edges_df_exploded with base_text_units (map text_unit_id → document_ids)
    merged_edges_base_df = edges_df_exploded.merge(
        base_text_units_exploded,  # Now contains document_ids
        left_on="text_unit_ids",   # text_unit_id maps to base_text_units.id
        right_on="id",             # id in base_text_units
        how="left"
    )

    # Ensure "id" is not dropped if it's needed
    if "id" in merged_edges_base_df.columns:
        merged_edges_base_df = merged_edges_base_df.drop(columns=["id"])  # Drop redundant id from base_text_units

    # Step 7: Merge with metadata (map document_ids → description, title, source)
    merged_edges_metadata_df = merged_edges_base_df.merge(
        metadata_df,
        left_on="document_ids",  # Now we map document_ids to metadata
        right_on="id",
        how="left"
    )

    # Ensure "id" and "document_ids" are dropped only if they exist
    columns_to_drop = [col for col in ["document_ids", "id", "id_x", "id_y","text_y","text_x","analysis"] if col in merged_edges_metadata_df.columns]
    merged_edges_metadata_df = merged_edges_metadata_df.drop(columns=columns_to_drop)
    print("merged_edges_metadata_df columns:", merged_edges_metadata_df.columns)    # Step 8: Create NetworkX graph
    
    G = nx.from_pandas_edgelist(
        merged_edges_metadata_df,
        source="source",
        target="target",
        edge_attr=True  # Attach metadata as edge attributes
    )

    node_names = set(merged_edges_metadata_df["source"]).union(set(merged_edges_metadata_df["target"]))

    node_metadata = {}

    for _, row in merged_edges_metadata_df.iterrows():
        node_name = row["source"]  # The actual node name
        if node_name not in node_metadata:  # Avoid overwriting if duplicate rows exist
            node_metadata[node_name] = {
                "title": row.get("title", ""),  # Get the correct title column
                "description": row.get("description_y", ""),  # Get the correct description column
                "url": row.get("url", "")  # Renamed 'source' to 'url' from metadata
            }

        # Do the same for 'target' nodes
        node_name = row["target"]
        if node_name not in node_metadata:
            node_metadata[node_name] = {
                "title": row.get("title", ""),
                "description": row.get("description_y", ""),
                "url": row.get("url", "")
            }

    # Step 4: Assign metadata to nodes in the graph
    for node_name, metadata in node_metadata.items():
        if node_name in G.nodes:  # Ensure the node exists in the graph before adding metadata
            G.nodes[node_name]["title"] = metadata["title"]
            G.nodes[node_name]["description"] = metadata["description"]
            G.nodes[node_name]["url"] = metadata["url"]


    
    return G