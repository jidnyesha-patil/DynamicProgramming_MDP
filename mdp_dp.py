### MDP Value Iteration and Policy Iteration
### Reference: https://web.stanford.edu/class/cs234/assignment1/index.html 
import numpy as np

np.set_printoptions(precision=3)

"""
For policy_evaluation, policy_improvement, policy_iteration and value_iteration,
the parameters P, nS, nA, gamma are defined as follows:

	P: nested dictionary
		From gym.core.Environment
		For each pair of states in [1, nS] and actions in [1, nA], P[state][action] is a
		tuple of the form (probability, nextstate, reward, terminal) where
			- probability: float
				the probability of transitioning from "state" to "nextstate" with "action"
			- nextstate: int
				denotes the state we transition to (in range [0, nS - 1])
			- reward: int
				either 0 or 1, the reward for transitioning from "state" to
				"nextstate" with "action"
			- terminal: bool
			  True when "nextstate" is a terminal state (hole or goal), False otherwise
	nS: int
		number of states in the environment
	nA: int
		number of actions in the environment
	gamma: float
		Discount factor. Number in range [0, 1)
"""

def policy_evaluation(P, nS, nA, policy, gamma=0.9, tol=1e-8):
    """Evaluate the value function from a given policy.

    Parameters:
    ----------
    P, nS, nA, gamma:
        defined at beginning of file
    policy: np.array[nS,nA]
        The policy to evaluate. Maps states to actions.
    tol: float
        Terminate policy evaluation when
            max |value_function(s) - prev_value_function(s)| < tol
    Returns:
    -------
    value_function: np.ndarray[nS]
        The value function of the given policy, where value_function[s] is
        the value of state s
    """
    
    value_function = np.zeros(nS)
    ############################
    # IMPLEMENTATION #
    delta = np.Inf
    while delta>0:
        delta = 0
        for state in range(nS):
            this_v = value_function[state]
            action_sum = 0
            for action in range(nA):
                next_state_sum = 0
                for next_state in range(len(P[state][action])):
                    prob,next_s,reward,end = P[state][action][next_state]
                    if end:
                        value_function[next_s]=0
                    next_state_sum+= prob * (reward + gamma*value_function[next_s])
                action_sum+=policy[state][action]*next_state_sum
            value_function[state]=action_sum
            delta = max(delta,abs(this_v - value_function[state]))
    ############################
    return value_function


def policy_improvement(P, nS, nA, value_from_policy, gamma=0.9):
    """Given the value function from policy improve the policy.

    Parameters:
    -----------
    P, nS, nA, gamma:
        defined at beginning of file
    value_from_policy: np.ndarray
        The value calculated from the policy
    Returns:
    --------
    new_policy: np.ndarray[nS,nA]
        A 2D array of floats. Each float is the probability of the action
        to take in that state according to the environment dynamics and the 
        given value function.
    """

    new_policy = np.ones([nS, nA]) / nA
	############################
	# IMPLEMENTATION #
    for state in range(nS):
        for action in range(nA):
            old_prob = new_policy[state][action]
            next_state_sum = 0
            for next_state in range(len(P[state][action])):
                prob,next_s,reward,end = P[state][action][next_state]
                next_state_sum+= prob * (reward + gamma*value_from_policy[next_s])
            new_prob = next_state_sum
            new_policy[state][action] = new_prob    
        max_index = np.argmax(new_policy[state])
        new_policy[state]= np.zeros(nA)
        new_policy[state][max_index]=1.0
    ############################
    return new_policy


def policy_iteration(P, nS, nA, policy, gamma=0.9, tol=1e-8):
    """Runs policy iteration.

    You should call the policy_evaluation() and policy_improvement() methods to
    implement this method.

    Parameters
    ----------
    P, nS, nA, gamma:
        defined at beginning of file
    policy: policy to be updated
    tol: float
        tol parameter used in policy_evaluation()
    Returns:
    ----------
    new_policy: np.ndarray[nS,nA]
    V: np.ndarray[nS]
    """
    new_policy = policy.copy()
	############################
	# IMPLEMENTATION #
    policy_stable = False
    while not policy_stable:
        new_value_fxn = policy_evaluation(P, nS, nA, policy)
        new_policy = policy_improvement(P, nS, nA, new_value_fxn)
        if np.array_equal(new_policy,policy):
            policy_stable = True
            V = new_value_fxn
        else:
            policy_stable = False
            policy = new_policy
	############################
    return new_policy, V

def value_iteration(P, nS, nA, V, gamma=0.9, tol=1e-8):
    """
    Learn value function and policy by using value iteration method for a given
    gamma and environment.

    Parameters:
    ----------
    P, nS, nA, gamma:
        defined at beginning of file
    V: value to be updated
    tol: float
        Terminate value iteration when
            max |value_function(s) - prev_value_function(s)| < tol
    Returns:
    ----------
    policy_new: np.ndarray[nS,nA]
    V_new: np.ndarray[nS]
    """
    
    V_new = V.copy()
    ############################
    # IMPLEMENTATION #
    policy_new = np.zeros([nS, nA])
    error = 0
    error_list = np.zeros(nS)
    start = True
    while start or error > tol:
        start = False
        for state in range(nS):
            this_value = V_new[state]
            action_max = 0
            for action in range(nA):
                old_prob = policy_new[state][action]
                next_state_sum = 0
                for next_state in range(len(P[state][action])):
                    prob,next_s,reward,end = P[state][action][next_state]
                    if end:
                        V_new[next_s]=0.0
                    next_state_sum += prob * (reward + gamma*V_new[next_s])
                policy_new[state][action] = next_state_sum
                if action_max < next_state_sum:
                    action_max=next_state_sum
            max_index = np.argmax(policy_new[state])
            policy_new[state]= np.zeros(nA)
            policy_new[state][max_index]=1.0
            V_new[state]=action_max
            error_list[state]=abs(this_value - V_new[state])
        error = max(error_list)
    ############################
    return policy_new, V_new

def render_single(env, policy, render = False, n_episodes=100):
    """
    Given a game envrionemnt of gym package, play multiple episodes of the game.
    An episode is over when the returned value for "done" = True.
    At each step, pick an action and collect the reward and new state from the game.

    Parameters:
    ----------
    env: gym.core.Environment
      Environment to play on. Must have nS, nA, and P as attributes.
    policy: np.array of shape [env.nS, env.nA]
      The action to take at a given state
    render: whether or not to render the game(it's slower to render the game)
    n_episodes: the number of episodes to play in the game. 
    Returns:
    ------
    total_rewards: the total number of rewards achieved in the game.
    """
    total_rewards = 0
    for _ in range(n_episodes):
        ob = env.reset() # initialize the episode
        done = False
        while not done:
            if render:
                env.render() # render the game
            ############################
            # IMPLEMENTATION #
            action_possibilities = policy[ob]
            action = np.argmax(action_possibilities)
            ob , reward , done , _ = env.step(action)
            total_rewards+=reward
    
    return total_rewards



