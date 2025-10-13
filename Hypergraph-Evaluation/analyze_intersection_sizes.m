function analyze_intersection_sizes(hypergraph)

    edges = hypergraph.edges;
    num_edges = length(edges);
    node2edge = hypergraph.node2edge;
    
    size_cnt = containers.Map('KeyType', 'double', 'ValueType', 'double');
    
    fprintf('🔍 Computing intersection sizes by iterating through %d edges...\n', num_edges);
    fprintf('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

    for i = 1:num_edges

        counter = containers.Map('KeyType', 'double', 'ValueType', 'double');
        
        current_edge_nodes = edges{i}{2};

        for k = 1:length(current_edge_nodes)
            node = current_edge_nodes(k);

            if isKey(node2edge, node)
                past_edges = node2edge(node);

                for j = 1:length(past_edges)
                    past_edge_idx = past_edges(j);

                    if past_edge_idx < i
                        if isKey(counter, past_edge_idx)
                            counter(past_edge_idx) = counter(past_edge_idx) + 1;
                        else
                            counter(past_edge_idx) = 1;
                        end
                    end
                end
            end
        end
        
        all_intersection_sizes = values(counter);
        for k = 1:length(all_intersection_sizes)
            s = all_intersection_sizes{k};
            if isKey(size_cnt, s)
                size_cnt(s) = size_cnt(s) + 1;
            else
                size_cnt(s) = 1;
            end
        end

        % 更新进度条
        if mod(i, floor(num_edges/20)) == 0 || i == num_edges
            progress = i / num_edges * 100;
            fprintf('📈 Progress: %.0f%% (%d/%d edges processed)\n', progress, i, num_edges);
        end
    end
    fprintf('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    if size_cnt.Count > 0
        fprintf('🎯 Analysis completed! Processing results...\n');
        size_keys = cell2mat(keys(size_cnt));
        size_values = cell2mat(values(size_cnt));
        
        % 排序以便绘图和保存
        [sorted_keys, sort_idx] = sort(size_keys);
        sorted_values = size_values(sort_idx);

        fprintf('📊 Found %d distinct intersection sizes.\n', length(sorted_keys));
        
        if length(sorted_keys) >= 2
            fprintf('📈 Generating intersection size distribution plot...\n');
            plot_loglog_analysis(sorted_keys, sorted_values, 'Intersection size', 'Count');
        else
            fprintf('⚠️  Insufficient data for plot (need at least 2 distinct intersection sizes).\n');
        end
        
        if exist('results', 'dir') ~= 7
            mkdir('results');
        end
        result_data = [sorted_keys(:), sorted_values(:)];
        dlmwrite(sprintf('results/%s_intersection_sizes.txt', hypergraph.datatype), result_data, 'delimiter', '\t');
    else
        fprintf('❌ No intersections found.\n');
    end
    
end 