import pytest
from unittest.mock import patch, MagicMock
from src.app import main


class TestApp:
    @patch('src.app.time.sleep')
    @patch('src.app.RTSPProcessingService')
    def test_main_service_loop_runs_and_handles_keyboard_interrupt(self, mock_service_class, mock_sleep):
        # Setup
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        # Simulate KeyboardInterrupt after first loop

        def side_effect():
            raise KeyboardInterrupt()
        mock_service.process_frame.side_effect = side_effect
        mock_sleep.side_effect = [None]

        # Execute & Assert
        with pytest.raises(KeyboardInterrupt):
            main()
        mock_service.process_frame.assert_called_once()
        mock_service_class.assert_called_once()

    @patch('src.app.time.sleep')
    @patch('src.app.RTSPProcessingService')
    def test_main_service_loop_handles_exceptions(self, mock_service_class, mock_sleep):
        # Setup
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        # Simulate process_frame returning False (failure), then KeyboardInterrupt to break loop
        mock_service.process_frame.side_effect = [False, KeyboardInterrupt()]
        mock_sleep.side_effect = [None, None]

        # Execute & Assert
        with pytest.raises(KeyboardInterrupt):
            main()
        assert mock_service.process_frame.call_count == 2
        mock_service_class.assert_called_once()
