"""Tests for session memory functionality."""

import uuid
from unittest.mock import MagicMock, patch

from kosmo.agent import KosmoAgent


class TestSessionMemoryInit:
    """Tests for session memory initialization."""

    def test_init_default_enable_memory(self):
        """Test that agent defaults to enable_memory=True."""
        agent = KosmoAgent()
        assert agent.enable_memory is True

    def test_init_disable_memory(self):
        """Test that agent can be initialized with enable_memory=False."""
        agent = KosmoAgent(enable_memory=False)
        assert agent.enable_memory is False

    def test_init_has_thread_id(self):
        """Test that agent has a thread ID on init."""
        agent = KosmoAgent()
        assert agent._current_thread_id is not None
        assert len(agent._current_thread_id) > 0

    def test_init_thread_id_is_uuid(self):
        """Test that initial thread ID is a valid UUID."""
        agent = KosmoAgent()
        # Should not raise an exception
        uuid.UUID(agent._current_thread_id)

    def test_init_empty_sessions(self):
        """Test that sessions dict starts empty."""
        agent = KosmoAgent()
        assert agent._sessions == {}

    def test_init_checkpointer_lazy(self):
        """Test that checkpointer is not created until needed."""
        agent = KosmoAgent()
        assert agent._checkpointer is None


class TestCheckpointer:
    """Tests for checkpointer functionality."""

    def test_get_checkpointer_creates_on_demand(self):
        """Test that _get_checkpointer creates checkpointer when called."""
        agent = KosmoAgent()
        checkpointer = agent._get_checkpointer()
        assert checkpointer is not None
        assert agent._checkpointer is not None

    def test_get_checkpointer_returns_same_instance(self):
        """Test that _get_checkpointer returns cached instance."""
        agent = KosmoAgent()
        cp1 = agent._get_checkpointer()
        cp2 = agent._get_checkpointer()
        assert cp1 is cp2

    def test_get_checkpointer_none_when_disabled(self):
        """Test that _get_checkpointer returns None when memory disabled."""
        agent = KosmoAgent(enable_memory=False)
        checkpointer = agent._get_checkpointer()
        assert checkpointer is None

    def test_checkpointer_is_inmemory_saver(self):
        """Test that checkpointer is InMemorySaver instance."""
        from langgraph.checkpoint.memory import InMemorySaver
        agent = KosmoAgent()
        checkpointer = agent._get_checkpointer()
        assert isinstance(checkpointer, InMemorySaver)


class TestThreadIdManagement:
    """Tests for thread ID management methods."""

    def test_get_current_thread_id(self):
        """Test get_current_thread_id returns current thread ID."""
        agent = KosmoAgent()
        thread_id = agent.get_current_thread_id()
        assert thread_id == agent._current_thread_id

    def test_set_thread_id(self):
        """Test set_thread_id changes current thread ID."""
        agent = KosmoAgent()
        new_thread = "custom-thread-123"
        agent.set_thread_id(new_thread)
        assert agent._current_thread_id == new_thread

    def test_new_session_creates_new_thread(self):
        """Test new_session creates a new thread ID."""
        agent = KosmoAgent()
        original_thread = agent.get_current_thread_id()
        new_thread = agent.new_session()
        assert new_thread != original_thread
        assert agent.get_current_thread_id() == new_thread

    def test_new_session_returns_valid_uuid(self):
        """Test new_session returns a valid UUID."""
        agent = KosmoAgent()
        new_thread = agent.new_session()
        # Should not raise an exception
        uuid.UUID(new_thread)

    def test_new_session_clears_messages(self):
        """Test new_session clears message history."""
        agent = KosmoAgent()
        agent.messages = [{"role": "user", "content": "test"}]
        agent.new_session()
        assert agent.messages == []


class TestSessionTracking:
    """Tests for session tracking functionality."""

    def test_get_session_info_returns_none_for_unknown(self):
        """Test get_session_info returns None for unknown thread."""
        agent = KosmoAgent()
        info = agent.get_session_info("unknown-thread")
        assert info is None

    def test_get_session_info_uses_current_thread(self):
        """Test get_session_info uses current thread if not specified."""
        agent = KosmoAgent()
        # Simulate a session being created
        agent._sessions[agent._current_thread_id] = {"test": True}
        info = agent.get_session_info()
        assert info is not None
        assert info["test"] is True

    def test_list_sessions_empty_initially(self):
        """Test list_sessions returns empty dict initially."""
        agent = KosmoAgent()
        sessions = agent.list_sessions()
        assert sessions == {}

    def test_list_sessions_returns_copy(self):
        """Test list_sessions returns a copy, not the original."""
        agent = KosmoAgent()
        agent._sessions["test-thread"] = {"test": True}
        sessions = agent.list_sessions()
        sessions["test-thread"]["modified"] = True
        # Original should not be modified
        assert "modified" not in agent._sessions["test-thread"]


class TestQueryWithThreadId:
    """Tests for query with thread_id parameter."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_query_uses_current_thread_by_default(self, mock_llm_class, mock_create_agent):
        """Test that query uses current thread ID by default."""
        mock_agent = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_message.type = "ai"
        mock_agent.invoke.return_value = {"messages": [mock_message]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        current_thread = agent.get_current_thread_id()
        agent.query("Test query")

        # Check that config included the current thread_id
        call_config = mock_agent.invoke.call_args[1]["config"]
        assert "configurable" in call_config
        assert call_config["configurable"]["thread_id"] == current_thread

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_query_uses_provided_thread_id(self, mock_llm_class, mock_create_agent):
        """Test that query uses provided thread ID when specified."""
        mock_agent = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_message.type = "ai"
        mock_agent.invoke.return_value = {"messages": [mock_message]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        custom_thread = "custom-thread-456"
        agent.query("Test query", thread_id=custom_thread)

        # Check that config included the custom thread_id
        call_config = mock_agent.invoke.call_args[1]["config"]
        assert call_config["configurable"]["thread_id"] == custom_thread

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_query_no_thread_when_memory_disabled(self, mock_llm_class, mock_create_agent):
        """Test that query doesn't include thread_id when memory disabled."""
        mock_agent = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_message.type = "ai"
        mock_agent.invoke.return_value = {"messages": [mock_message]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, enable_memory=False)
        agent.query("Test query")

        # Check that config does not include configurable
        call_config = mock_agent.invoke.call_args[1]["config"]
        assert "configurable" not in call_config

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_query_tracks_session(self, mock_llm_class, mock_create_agent):
        """Test that query creates session tracking info."""
        mock_agent = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_message.type = "ai"
        mock_agent.invoke.return_value = {"messages": [mock_message]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        agent.query("Test query")

        # Check session was tracked
        session_info = agent.get_session_info()
        assert session_info is not None
        assert "created_at" in session_info
        assert "query_count" in session_info
        assert session_info["query_count"] == 1

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_query_increments_query_count(self, mock_llm_class, mock_create_agent):
        """Test that query increments session query count."""
        mock_agent = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_message.type = "ai"
        mock_agent.invoke.return_value = {"messages": [mock_message]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        agent.query("First query")
        agent.query("Second query")

        session_info = agent.get_session_info()
        assert session_info["query_count"] == 2

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_query_updates_last_query_time(self, mock_llm_class, mock_create_agent):
        """Test that query updates last_query_at timestamp."""
        mock_agent = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_message.type = "ai"
        mock_agent.invoke.return_value = {"messages": [mock_message]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        agent.query("Test query")

        session_info = agent.get_session_info()
        assert "last_query_at" in session_info
        assert session_info["last_query_at"] >= session_info["created_at"]


class TestAgentWithCheckpointer:
    """Tests for agent creation with checkpointer."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_agent_created_with_checkpointer(self, mock_llm_class, mock_create_agent):
        """Test that ReAct agent is created with checkpointer when enabled."""
        mock_agent = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Test"
        mock_message.type = "ai"
        mock_agent.invoke.return_value = {"messages": [mock_message]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        agent.query("Test")

        # Check create_react_agent was called with checkpointer
        call_kwargs = mock_create_agent.call_args[1]
        assert "checkpointer" in call_kwargs
        assert call_kwargs["checkpointer"] is not None

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_agent_created_without_checkpointer_when_disabled(
        self, mock_llm_class, mock_create_agent
    ):
        """Test that ReAct agent is created without checkpointer when disabled."""
        mock_agent = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Test"
        mock_message.type = "ai"
        mock_agent.invoke.return_value = {"messages": [mock_message]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False, enable_memory=False)
        agent.query("Test")

        # Check create_react_agent was called with checkpointer=None
        call_kwargs = mock_create_agent.call_args[1]
        assert call_kwargs["checkpointer"] is None


class TestMultiTurnConversation:
    """Tests for multi-turn conversation with session memory."""

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_same_thread_used_across_queries(self, mock_llm_class, mock_create_agent):
        """Test that same thread ID is used for consecutive queries."""
        mock_agent = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Response"
        mock_message.type = "ai"
        mock_agent.invoke.return_value = {"messages": [mock_message]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        agent.query("First question")
        first_thread = mock_agent.invoke.call_args[1]["config"]["configurable"]["thread_id"]

        agent.query("Follow-up question")
        second_thread = mock_agent.invoke.call_args[1]["config"]["configurable"]["thread_id"]

        assert first_thread == second_thread

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_new_session_creates_new_thread(self, mock_llm_class, mock_create_agent):
        """Test that new_session changes the thread ID for subsequent queries."""
        mock_agent = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Response"
        mock_message.type = "ai"
        mock_agent.invoke.return_value = {"messages": [mock_message]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)
        agent.query("First question")
        first_thread = mock_agent.invoke.call_args[1]["config"]["configurable"]["thread_id"]

        agent.new_session()
        agent.query("New conversation")
        second_thread = mock_agent.invoke.call_args[1]["config"]["configurable"]["thread_id"]

        assert first_thread != second_thread

    @patch("kosmo.agent.create_react_agent")
    @patch("kosmo.agent.ChatOpenAI")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_multiple_sessions_tracked(self, mock_llm_class, mock_create_agent):
        """Test that multiple sessions are tracked separately."""
        mock_agent = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Response"
        mock_message.type = "ai"
        mock_agent.invoke.return_value = {"messages": [mock_message]}
        mock_create_agent.return_value = mock_agent

        agent = KosmoAgent(verbose=False)

        # First session
        first_thread = agent.get_current_thread_id()
        agent.query("Query 1")
        agent.query("Query 2")

        # Second session
        second_thread = agent.new_session()
        agent.query("Query 3")

        sessions = agent.list_sessions()
        assert len(sessions) == 2
        assert first_thread in sessions
        assert second_thread in sessions
        assert sessions[first_thread]["query_count"] == 2
        assert sessions[second_thread]["query_count"] == 1
