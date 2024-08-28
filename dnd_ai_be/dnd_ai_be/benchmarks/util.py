import os
import datetime
import mlflow
import os
from functools import wraps


def test_mlflow_connection_and_logging():
    """
    Test MLflow connection and logging by creating a test run,
    logging a parameter, and logging a sample artifact.
    """
    # Define test parameters and artifact
    test_param = "test_value"
    artifact_content = "This is a test artifact content."

    # Create a temporary artifact file
    artifact_file_path = "test_artifact.txt"
    with open(artifact_file_path, "w") as f:
        f.write(artifact_content)

    # Start MLflow run
    with mlflow.start_run() as run:
        mlflow.log_param("test_param", test_param)
        mlflow.log_artifact(artifact_file_path)
        print(f"Test run completed. Run ID: {run.info.run_id}")
    os.remove(artifact_file_path)


def track_with_mlflow(experiment_name, verbose=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if experiment_name:
                mlflow.set_experiment(experiment_name)
                if verbose:
                    print(f"Set experiment to {experiment_name}")

            with mlflow.start_run() as run:
                # LOG ARGS
                for key, value in kwargs.items():
                    mlflow.log_param(key, value)
                    if verbose:
                        print(f"logging param: {key}, {value}")

                # DO RUN
                result = func(*args, **kwargs)

                output_file_path = result.get("output_file_path")
                if output_file_path and os.path.exists(output_file_path):
                    mlflow.log_artifact(output_file_path)
                    if verbose:
                        print(f"logging artifact: {output_file_path}")
                return result

        return wrapper

    return decorator


# def log_args(args: dict):
#     """
#     Parse command-line arguments and log them to MLflow.
#     """
#     # Start MLflow run
#     with mlflow.start_run() as run:
#         # Log each argument as a parameter
#         for key, value in args.items():
#             if value is not None:  # Log only if the value is not None
#                 mlflow.log_param(key, value)

#         print(f"Arguments logged. Run ID: {run.info.run_id}")


if __name__ == "__main__":
    # @track_with_mlflow(experiment_name="tmp")
    # def main():
    #     print("hello world")

    # main()
    pass
