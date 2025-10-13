function analyze_group_degrees(hypergraph)

    fprintf('Analyzing heavy-tailed group degree distribution (v2.1, fixed nchoosek)...\n');
    
    edges = hypergraph.edges;
    num_edges = length(edges);
    
    fprintf('📊 Dataset info: %d edges\n', num_edges);
    
    group_counts = containers.Map('KeyType', 'char', 'ValueType', 'double');
    
    fprintf('\n🔍 Computing group occurrences by iterating through edges...\n');
    fprintf('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    for i = 1:num_edges
        if mod(i, max(1, floor(num_edges/10))) == 0 || i == num_edges
            fprintf('📈 Progress: %.0f%% (%d/%d edges processed)\n', 100*i/num_edges, i, num_edges);
        end
        
        hyperedge_nodes = edges{i}{2}; % 这是数值数组
        num_nodes_in_edge = length(hyperedge_nodes);
        
        if num_nodes_in_edge >= 2
            pairs = nchoosek(hyperedge_nodes, 2);
            for p_idx = 1:size(pairs, 1)
                pair = sort(pairs(p_idx, :));
                key = sprintf('%d-%d', pair(1), pair(2));
                if isKey(group_counts, key)
                    group_counts(key) = group_counts(key) + 1;
                else
                    group_counts(key) = 1;
                end
            end
        end
        
        if num_nodes_in_edge >= 3
            if num_nodes_in_edge > 20
                sample_nodes = hyperedge_nodes(randperm(num_nodes_in_edge, 20));
            else
                sample_nodes = hyperedge_nodes;
            end
            
            triples = nchoosek(sample_nodes, 3);
            for t_idx = 1:size(triples, 1)
                triple = sort(triples(t_idx, :));
                key = sprintf('%d-%d-%d', triple(1), triple(2), triple(3));
                if isKey(group_counts, key)
                    group_counts(key) = group_counts(key) + 1;
                else
                    group_counts(key) = 1;
                end
            end
        end
    end
    
    fprintf('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    fprintf('🎯 Analysis completed! Processing results...\n');
    
    if isempty(group_counts)
        fprintf('❌ Warning: No node groups found.\n');
        return;
    end
    
    group_degrees = cell2mat(values(group_counts));
    
    if ~isempty(group_degrees)
        fprintf('📊 Found %d unique node groups\n', length(group_degrees));
        
        [unique_degrees, ~, idx] = unique(group_degrees);
        counts = accumarray(idx, 1);
        degrees = double(unique_degrees);
        freq = double(counts);
        
        if length(degrees) >= 2
            plot_loglog_analysis(degrees, freq, 'Group degree', 'Count');
        else
            fprintf('⚠️  Insufficient data for plot.\n');
        end
        
        if exist('results', 'dir') ~= 7
            mkdir('results');
        end
        % [修复] 确保两个数组都是列向量以便拼接
        result_data = [degrees(:), freq(:)];
        dlmwrite(sprintf('results/%s_group_degrees.txt', hypergraph.datatype), result_data, 'delimiter', '\t');
    else
        fprintf('❌ Warning: No valid group degrees found.\n');
    end
    
end 