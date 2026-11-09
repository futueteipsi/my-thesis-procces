clear; clc; close all;

% model parameters
grid_size = 100;
time_steps = 200;
density = 0.6; % плотность населения
initial_infected = 5;

p_infect = 0.30; % prob to infect in contact with 1 I
p_recover = 0.08; % prob to cure in one step

% initialization cell state
% empty net
grid = ones(grid_size, grid_size);

% put people (state 0)
num_cells = grid_size * grid_size;
num_people = round(num_cells * density);
people_indices = randperm(num_cells, num_people);
grid(people_indices) = 0;

% infect random (state 2)
infected_indices = people_indices(randperm(num_people, initial_infected));
grid(infected_indices) = 2;

% arrays for preserving the epidemic's chronology
history_S = zeros(1, time_steps);
history_I = zeros(1, time_steps);
history_R = zeros(1, time_steps);

% set vizual
figure('Name', 'Epidemic modeling', ...
       'Position', [100, 100, 1000, 450], 'NumberTitle', 'off');

% state colors: 0-blue, 1-grey, 2-red, 3-green
custom_colormap = [
    0.0, 0.4, 0.8; ...
    0.9, 0.9, 0.9; ... 
    0.8, 0.0, 0.0; ... 
    0.0, 0.6, 0.0
];
colormap(custom_colormap);

% time
for t = 1:time_steps
    new_grid = grid;    
    % current data
    history_S(t) = sum(grid(:) == 0);
    history_I(t) = sum(grid(:) == 2);
    history_R(t) = sum(grid(:) == 3);
    
    % real time
    % left plot: net map
    subplot(1, 2, 1);
    imagesc(grid, [0 3]);
    axis square;
    title(sprintf('Cell space, (day %d)', t));
    xlabel('X'); ylabel('Y');
    
    % right: SIR epidemic curve
    subplot(1, 2, 2);
    plot(1:t, history_S(1:t), 'b-', 'LineWidth', 1.5); hold on;
    plot(1:t, history_I(1:t), 'r-', 'LineWidth', 2.0);
    plot(1:t, history_R(1:t), 'g-', 'LineWidth', 1.5);
    hold off;
    grid on;
    title('Dynamics of SIR indicators');
    xlabel('Time (days)'); ylabel('People quantity');
    legend('S', 'I', 'R', ...
           'Location', 'northeast');
    
    drawnow;
    
    % check when epidemic over
    if history_I(t) == 0
        fprintf('The epidemic over on the %d-th day.\n', t);
        history_S(t:end) = history_S(t);
        history_I(t:end) = 0;
        history_R(t:end) = history_R(t);
        break;
    end
    
    % every cell
    for i = 1:grid_size
        for j = 1:grid_size
            current_state = grid(i, j);
            
            % A: 0 can be infected
            if current_state == 0
                num_infected_neighbors = 0;
                
                % visiting 8 neighbors (Moore neighborhood)
                for di = -1:1
                    for dj = -1:1
                        if di == 0 && dj == 0, continue; end % skip ourselves
                        
                        ni = i + di;
                        nj = j + dj;
                        
                        % check net border
                        if ni >= 1 && ni <= grid_size && nj >= 1 && nj <= grid_size
                            if grid(ni, nj) == 2
                                num_infected_neighbors = num_infected_neighbors + 1;
                            end
                        end
                    end
                end
                
                % prob to be infected
                if num_infected_neighbors > 0
                    p_get_sick = 1 - (1 - p_infect)^num_infected_neighbors;
                    
                    if rand() < p_get_sick
                        new_grid(i, j) = 2;
                    end
                end
                
            % B: 2 can be cured
            elseif current_state == 2
                if rand() < p_recover
                    new_grid(i, j) = 3; % cell cured and become imune
                end
            end
        end
    end

    grid = new_grid;
end