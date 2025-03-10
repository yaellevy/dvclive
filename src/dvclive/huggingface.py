from typing import Optional

from transformers import (
    TrainerCallback,
    TrainerControl,
    TrainerState,
    TrainingArguments,
)
from transformers.trainer import Trainer

from dvclive import Live
from dvclive.utils import standardize_metric_name


class DVCLiveCallback(TrainerCallback):
    def __init__(self, model_file=None, live: Optional[Live] = None, **kwargs):
        super().__init__()
        self.model_file = model_file
        self.live = live if live is not None else Live(**kwargs)

    def on_log(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs
    ):
        logs = kwargs["logs"]
        for key, value in logs.items():
            self.live.log_metric(standardize_metric_name(key, __name__), value)
        self.live.next_step()

    def on_epoch_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs
    ):
        if self.model_file:
            model = kwargs["model"]
            model.save_pretrained(self.model_file)
            tokenizer = kwargs.get("tokenizer")
            if tokenizer:
                tokenizer.save_pretrained(self.model_file)
            self.live.log_artifact(self.model_file)

    def on_train_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs
    ):
        if args.load_best_model_at_end:
            trainer = Trainer(
                args=args, model=kwargs.get("model"), tokenizer=kwargs.get("tokenizer")
            )
            trainer.save_model()
            self.live.log_artifact(args.output_dir)
        self.live.end()
