function analyze_singular_values(hypergraph)

    fprintf('Analyzing singular values...\n');
    
    incidence_matrix = hypergraph.incidence_matrix;
    fprintf('Using pre-built incidence matrix of size %d x %d\n', ...
            size(incidence_matrix, 1), size(incidence_matrix, 2));
    
    k = min([100, size(incidence_matrix, 1), size(incidence_matrix, 2)]);
    fprintf('Computing SVD with rank %d...\n', k);
    
    try
        s = svds(incidence_matrix, k);
    catch ME
        fprintf('Error during SVD computation: %s\n', ME.message);
        fprintf('Attempting with full matrix...\n');
        try
            s = svd(full(incidence_matrix));
        catch ME_full
            fprintf('Full SVD also failed: %s\n', ME_full.message);
            return;
        end
    end

    if ~isempty(s)
        ranks = 1:length(s);
        if length(ranks) >= 2
            plot_loglog_analysis(ranks, s, 'Rank', 'Singular value');
        else
            fprintf('⚠️  Insufficient data for plot (need at least 2 singular values).\n');
        end
        
        if ~exist('results', 'dir')
            mkdir('results');
        end
        
        fid = fopen(sprintf('results/%s_singular_values.txt', hypergraph.datatype), 'w');
        for i = 1:length(s)
            fprintf(fid, '%d %.6f\n', i, s(i));
        end
        fclose(fid);
    end
    
    fprintf('Singular value analysis completed.\n');
end 