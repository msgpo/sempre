package edu.stanford.nlp.sempre;

import fig.basic.LogInfo;
import fig.basic.Option;
import fig.exec.Execution;

/**
 * Entry point for the semantic parser.
 *
 * @author Percy Liang
 */
public class Main implements Runnable {
	@Option
	public boolean interactive = false;
	@Option
	public boolean server = false;
	@Option
	public boolean streamapi = false;

	public void run() {
		Builder builder = new Builder();
		builder.build();

		Dataset dataset = new Dataset();
		dataset.read();

		Learner learner = new Learner(builder.parser, builder.params, dataset);
		learner.learn();

		if (server) {
			Master master = new Master(builder);
			Server server = new Server(master);
			server.run();
		}

		if (interactive) {
			Master master = new Master(builder);
			master.runInteractivePrompt();
		}

		if (streamapi) {
			Master master = new Master(builder);
			StreamAPI stream = new StreamAPI(master, builder);
			stream.run();
		}
	}

	public static void main(String[] args) {
		LogInfo.writeToStdout = false;
		Execution.run(args, "Main", new Main(), Master.getOptionsParser());
	}
}
