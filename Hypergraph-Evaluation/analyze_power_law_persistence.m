function analyze_power_law_persistence(hypergraph)

    fprintf('Analyzing power-law persistence...\n');
    
    edges = hypergraph.edges;
    num_edges = length(edges);
    
    fprintf('📊 Dataset info: %d edges\n', num_edges);
    
    node_group_persistence = containers.Map('KeyType', 'char', 'ValueType', 'int32');
    
    max_edges_to_analyze = min(num_edges, 2000);
    fprintf('🔄 Analysis limit: %d edges\n', max_edges_to_analyze);
    
    fprintf('\n🔍 Computing node group occurrences...\n');
    fprintf('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    for i = 1:max_edges_to_analyze
        if mod(i, 200) == 0
            fprintf('📈 Progress: %.0f%%\n', 100 * i / max_edges_to_analyze);
        end
        
        edge_nodes = edges{i}{2};
        
        if length(edge_nodes) >= 2
            pairs = nchoosek(edge_nodes, 2);
            for p_idx = 1:size(pairs, 1)
                key = sprintf('%d_%d', sort(pairs(p_idx, :)));
                if isKey(node_group_persistence, key)
                    node_group_persistence(key) = node_group_persistence(key) + 1;
                else
                    node_group_persistence(key) = 1;
                end
            end
        end
        
        if length(edge_nodes) >= 3
            if length(edge_nodes) > 10
                sample_nodes = edge_nodes(randperm(length(edge_nodes), 10));
            else
                sample_nodes = edge_nodes;
            end
            triples = nchoosek(sample_nodes, 3);
            for t_idx = 1:size(triples, 1)
                key = sprintf('%d_%d_%d', sort(triples(t_idx, :)));
                if isKey(node_group_persistence, key)
                    node_group_persistence(key) = node_group_persistence(key) + 1;
                else
                    node_group_persistence(key) = 1;
                end
            end
        end
    end
    
    fprintf('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    persistence_values = cell2mat(values(node_group_persistence));
    
    if ~isempty(persistence_values)
        persistent_groups = persistence_values(persistence_values > 1);
        
        if ~isempty(persistent_groups)
            [unique_persistence, ~, idx] = unique(persistent_groups);
            counts = accumarray(idx, 1);
            
            persistence = double(unique_persistence);
            freq = double(counts);
            
            if length(persistence) >= 2
                plot_loglog_analysis(persistence, freq, 'Persistence value', 'Count');
            else
                fprintf('⚠️  Insufficient data for plot.\n');
            end
            
            if exist('results', 'dir') ~= 7
                mkdir('results');
            end
            
            result_data = [persistence(:), freq(:)];
            dlmwrite(sprintf('results/%s_power_law_persistence.txt', hypergraph.datatype), result_data, 'delimiter', '\t');
        end
    end
    
end 