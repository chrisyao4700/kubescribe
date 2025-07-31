from typing import Optional, Dict, Any
from kubernetes import client, config
from uuid import uuid4
import os

class K8sJobClient:
    def __init__(self, namespace: str):
        # Load config (in-cluster or from kubeconfig)
        try:
            config.load_incluster_config()
        except Exception:
            config.load_kube_config()
        self.namespace = namespace
        self.api = client.BatchV1Api()

    def create_core_runner_job(self, *, image: str, env_from_secret: str, backoff_limit: int = 0,
                               ttl_seconds: int = 600, run_id: Optional[str] = None,
                               trigger: str = "api", source: str = "k8s") -> Dict[str, Any]:
        rid = run_id or str(uuid4())
        name = f"core-runner-{rid[:8]}"
        labels = {"app": "core-runner", "run_id": rid}

        container = client.V1Container(
            name="core-runner",
            image=image,
            image_pull_policy="IfNotPresent",
            env=[
                client.V1EnvVar(name="RUN_TRIGGER", value=trigger),
                client.V1EnvVar(name="RUN_SOURCE", value=source),
                client.V1EnvVar(name="RUN_ID", value=rid),
            ],
            env_from=[client.V1EnvFromSource(secret_ref=client.V1SecretEnvSource(name=env_from_secret))],
        )

        pod_spec = client.V1PodSpec(
            restart_policy="Never",
            containers=[container],
            service_account_name=os.environ.get("SERVICE_ACCOUNT_NAME")  # optional
        )

        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels=labels),
            spec=pod_spec
        )

        job_spec = client.V1JobSpec(
            template=template,
            backoff_limit=backoff_limit,
            ttl_seconds_after_finished=ttl_seconds
        )

        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name=name, labels=labels),
            spec=job_spec
        )

        created = self.api.create_namespaced_job(namespace=self.namespace, body=job)
        return {"job_name": created.metadata.name, "run_id": rid}
